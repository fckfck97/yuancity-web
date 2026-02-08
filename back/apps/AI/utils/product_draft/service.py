import json
import os
import re
import requests

FIELDS_ORDER = ["nombre", "descripcion", "categoria", "precio", "stock", "descuento"]

LANGUAGE_NAMES = {
    "es": "español",
    "en": "inglés",
    "it": "italiano",
    "pt": "portugués",
    "zh": "chino",
}

FIELD_LABELS = {
    "es": {
        "nombre": "nombre",
        "descripcion": "descripción",
        "categoria": "categoría",
        "precio": "precio",
        "stock": "cantidad",
        "descuento": "descuento",
    },
    "en": {
        "nombre": "name",
        "descripcion": "description",
        "categoria": "category",
        "precio": "price",
        "stock": "quantity",
        "descuento": "discount",
    },
    "it": {
        "nombre": "nome",
        "descripcion": "descrizione",
        "categoria": "categoria",
        "precio": "prezzo",
        "stock": "quantità",
        "descuento": "sconto",
    },
    "pt": {
        "nombre": "nome",
        "descripcion": "descrição",
        "categoria": "categoria",
        "precio": "preço",
        "stock": "quantidade",
        "descuento": "desconto",
    },
    "zh": {
        "nombre": "名称",
        "descripcion": "描述",
        "categoria": "类别",
        "precio": "价格",
        "stock": "数量",
        "descuento": "折扣",
    },
}

ERROR_MESSAGES = {
    "es": {
        "nombre": "El nombre debe tener al menos 3 caracteres.",
        "descripcion": "La descripción debe tener al menos 10 caracteres.",
        "categoria": "La categoría es obligatoria.",
        "precio": "El precio debe ser un número mayor a 0.",
        "stock": "La cantidad debe ser un número entero mayor o igual a 1.",
        "descuento": "El descuento debe estar entre 0 y 90.",
        "descuento_formato": "El descuento debe ser un número entre 0 y 90.",
    },
    "en": {
        "nombre": "The name must have at least 3 characters.",
        "descripcion": "The description must have at least 10 characters.",
        "categoria": "Category is required.",
        "precio": "Price must be a number greater than 0.",
        "stock": "Quantity must be an integer greater than or equal to 1.",
        "descuento": "Discount must be between 0 and 90.",
        "descuento_formato": "Discount must be a number between 0 and 90.",
    },
    "it": {
        "nombre": "Il nome deve avere almeno 3 caratteri.",
        "descripcion": "La descrizione deve avere almeno 10 caratteri.",
        "categoria": "La categoria è obbligatoria.",
        "precio": "Il prezzo deve essere un numero maggiore di 0.",
        "stock": "La quantità deve essere un intero maggiore o uguale a 1.",
        "descuento": "Lo sconto deve essere tra 0 e 90.",
        "descuento_formato": "Lo sconto deve essere un numero tra 0 e 90.",
    },
    "pt": {
        "nombre": "O nome deve ter pelo menos 3 caracteres.",
        "descripcion": "A descrição deve ter pelo menos 10 caracteres.",
        "categoria": "A categoria é obrigatória.",
        "precio": "O preço deve ser um número maior que 0.",
        "stock": "A quantidade deve ser um inteiro maior ou igual a 1.",
        "descuento": "O desconto deve estar entre 0 e 90.",
        "descuento_formato": "O desconto deve ser um número entre 0 e 90.",
    },
    "zh": {
        "nombre": "名称至少需要 3 个字符。",
        "descripcion": "描述至少需要 10 个字符。",
        "categoria": "类别为必填项。",
        "precio": "价格必须是大于 0 的数字。",
        "stock": "数量必须是大于等于 1 的整数。",
        "descuento": "折扣必须在 0 到 90 之间。",
        "descuento_formato": "折扣必须是 0 到 90 的数字。",
    },
}


def default_draft():
    return {key: None for key in FIELDS_ORDER}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_digits(value: str) -> str:
    return re.sub(r"\D+", "", value or "")


def normalize_value(field: str, value: str) -> str:
    if field in {"nombre", "descripcion", "categoria"}:
        return normalize_text(value)
    if field in {"precio", "stock", "descuento"}:
        return normalize_digits(value)
    return normalize_text(value)


def normalize_language(value: str | None) -> str:
    if not value:
        return "es"
    code = value.split("-")[0].lower()
    return code if code in LANGUAGE_NAMES else "es"


def validate_field(field: str, value: str, language: str):
    messages = ERROR_MESSAGES.get(language, ERROR_MESSAGES["es"])
    if field == "nombre":
        if len(value) < 3:
            return False, messages["nombre"]
    elif field == "descripcion":
        if len(value) < 10:
            return False, messages["descripcion"]
    elif field == "categoria":
        if not value:
            return False, messages["categoria"]
    elif field == "precio":
        if not value or not value.isdigit() or int(value) <= 0:
            return False, messages["precio"]
    elif field == "stock":
        if not value or not value.isdigit() or int(value) < 1:
            return False, messages["stock"]
    elif field == "descuento":
        if not value:
            return True, None
        if not value.isdigit():
            return False, messages["descuento_formato"]
        num = int(value)
        if num < 0 or num > 90:
            return False, messages["descuento"]
    return True, None


def build_system_prompt(language: str):
    language_name = LANGUAGE_NAMES.get(language, "español")
    return (
        "Eres un asistente de registro de productos. Debes llenar exactamente estos "
        "campos en este orden: nombre, descripcion, categoria, precio, stock, descuento. "
        "Reglas: pregunta SOLO por el campo faltante (next_field). "
        "Valida: nombre min 3 caracteres, descripcion min 10, categoria no vacía, "
        "precio número > 0, stock entero >=1, descuento 0-90. "
        "Si el usuario envía algo inválido, explica el error y vuelve a pedir el MISMO campo. "
        "Cuando esté todo completo, confirma con un resumen corto y marca is_complete=true. "
        "Obligatorio: SIEMPRE llama a la herramienta update_product_draft con JSON completo. "
        f"Responde en {language_name}."
    )


def tool_schema():
    return {
        "type": "function",
        "name": "update_product_draft",
        "description": "Actualiza el borrador del producto y define el siguiente campo a solicitar.",
        "strict": True,
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "field": {"type": "string", "enum": FIELDS_ORDER},
                "value": {"type": "string"},
                "normalized": {"type": ["string", "null"]},
                "is_valid": {"type": "boolean"},
                "error": {"type": ["string", "null"]},
                "draft": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "nombre": {"type": ["string", "null"]},
                        "descripcion": {"type": ["string", "null"]},
                        "categoria": {"type": ["string", "null"]},
                        "precio": {"type": ["string", "null"]},
                        "stock": {"type": ["string", "null"]},
                        "descuento": {"type": ["string", "null"]},
                    },
                    "required": [
                        "nombre",
                        "descripcion",
                        "categoria",
                        "precio",
                        "stock",
                        "descuento",
                    ],
                },
                "next_field": {
                    "type": ["string", "null"],
                    "enum": FIELDS_ORDER + [None],
                },
                "is_complete": {"type": "boolean"},
            },
            "required": [
                "field",
                "value",
                "normalized",
                "is_valid",
                "error",
                "draft",
                "next_field",
                "is_complete",
            ],
        },
    }


def ask_openai(message: str, draft: dict, next_field: str, language: str):
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("APIKEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY no está configurada.")

    language = normalize_language(language)
    context = {
        "draft": draft,
        "next_field": next_field,
        "user_message": message,
        "language": language,
    }

    payload = {
        "model": "gpt-4.1-mini",
        "input": [
            {"role": "system", "content": build_system_prompt(language)},
            {
                "role": "user",
                "content": f"Contexto JSON: {json.dumps(context, ensure_ascii=False)}",
            },
        ],
        "tools": [tool_schema()],
        "tool_choice": {"type": "function", "name": "update_product_draft"},
    }

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=40,
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"OpenAI error {response.status_code}: {response.text}"
        )

    data = response.json()
    output = data.get("output", [])
    for item in output:
        if item.get("type") in {"function_call", "tool_call"}:
            if item.get("name") == "update_product_draft":
                args = item.get("arguments")
                if isinstance(args, str):
                    return json.loads(args)
                return args

    raise RuntimeError("El modelo no devolvió la llamada de herramienta.")


def update_draft_with_validation(current_draft: dict, next_field: str, args: dict, language: str):
    language = normalize_language(language)
    draft = default_draft()
    draft.update(current_draft or {})

    field = next_field
    raw_value = ""
    if isinstance(args, dict):
        raw_value = args.get("value") or ""

    normalized = normalize_value(field, raw_value)
    is_valid, error = validate_field(field, normalized, language)

    if is_valid:
        if field == "descuento" and normalized == "":
            draft[field] = "0"
        else:
            draft[field] = normalized

    next_missing = None
    for key in FIELDS_ORDER:
        if not draft.get(key):
            next_missing = key
            break

    is_complete = next_missing is None

    return {
        "draft": draft,
        "field": field,
        "value": raw_value,
        "normalized": normalized,
        "is_valid": is_valid,
        "error": error,
        "next_field": next_missing,
        "is_complete": is_complete,
        "language": language,
    }


def build_reply(result: dict):
    language = normalize_language(result.get("language"))
    labels = FIELD_LABELS.get(language, FIELD_LABELS["es"])
    draft = result.get("draft") or {}
    if result.get("is_complete"):
        if language == "en":
            return (
                "Perfect. I have everything:\n"
                f"- Name: {draft.get('nombre')}\n"
                f"- Description: {draft.get('descripcion')}\n"
                f"- Category: {draft.get('categoria')}\n"
                f"- Price: {draft.get('precio')}\n"
                f"- Quantity: {draft.get('stock')}\n"
                f"- Discount: {draft.get('descuento')}\n"
                "I will save the draft."
            )
        if language == "it":
            return (
                "Perfetto. Ho tutto:\n"
                f"- Nome: {draft.get('nombre')}\n"
                f"- Descrizione: {draft.get('descripcion')}\n"
                f"- Categoria: {draft.get('categoria')}\n"
                f"- Prezzo: {draft.get('precio')}\n"
                f"- Quantità: {draft.get('stock')}\n"
                f"- Sconto: {draft.get('descuento')}\n"
                "Salvo la bozza."
            )
        if language == "pt":
            return (
                "Perfeito. Já tenho tudo:\n"
                f"- Nome: {draft.get('nombre')}\n"
                f"- Descrição: {draft.get('descripcion')}\n"
                f"- Categoria: {draft.get('categoria')}\n"
                f"- Preço: {draft.get('precio')}\n"
                f"- Quantidade: {draft.get('stock')}\n"
                f"- Desconto: {draft.get('descuento')}\n"
                "Vou salvar o rascunho."
            )
        if language == "zh":
            return (
                "太好了，我已经收齐了：\n"
                f"- 名称: {draft.get('nombre')}\n"
                f"- 描述: {draft.get('descripcion')}\n"
                f"- 类别: {draft.get('categoria')}\n"
                f"- 价格: {draft.get('precio')}\n"
                f"- 数量: {draft.get('stock')}\n"
                f"- 折扣: {draft.get('descuento')}\n"
                "我会保存草稿。"
            )
        return (
            "Perfecto. Ya tengo todo:\n"
            f"- Nombre: {draft.get('nombre')}\n"
            f"- Descripción: {draft.get('descripcion')}\n"
            f"- Categoría: {draft.get('categoria')}\n"
            f"- Precio: {draft.get('precio')}\n"
            f"- Cantidad: {draft.get('stock')}\n"
            f"- Descuento: {draft.get('descuento')}\n"
            "Confirmo y guardo el borrador."
        )

    if not result.get("is_valid") and result.get("error"):
        field_label = labels.get(result.get("field"), result.get("field"))
        if language == "en":
            return f"{result['error']}\n\nPlease send your {field_label} again."
        if language == "it":
            return f"{result['error']}\n\nPer favore invia di nuovo il/la {field_label}."
        if language == "pt":
            return f"{result['error']}\n\nEnvie novamente seu {field_label}."
        if language == "zh":
            return f"{result['error']}\n\n请重新发送你的{field_label}。"
        return f"{result['error']}\n\nVuelve a enviarme tu {field_label}."

    next_field = result.get("next_field") or result.get("field")
    field_label = labels.get(next_field, next_field)
    if language == "en":
        return f"Great. Now send your {field_label}."
    if language == "it":
        return f"Ottimo. Ora inviami il/la {field_label}."
    if language == "pt":
        return f"Certo. Agora envie seu {field_label}."
    if language == "zh":
        return f"好的。请发送你的{field_label}。"
    return f"Listo. Ahora envíame tu {field_label}."
