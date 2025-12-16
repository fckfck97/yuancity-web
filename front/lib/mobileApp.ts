const SITE_BASE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://yuancity.com";
const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME ?? "YuanCity";
const APP_SCHEME = process.env.NEXT_PUBLIC_APP_SCHEME ?? "yuancity";
const ANDROID_PACKAGE = process.env.NEXT_PUBLIC_ANDROID_PACKAGE ?? "com.ovalcampus.yuancity";
const PLAY_STORE_URL =
  process.env.NEXT_PUBLIC_PLAY_STORE_URL ??
  `https://play.google.com/store/apps/details?id=${ANDROID_PACKAGE}`;
const APP_STORE_ID = process.env.NEXT_PUBLIC_APP_STORE_ID ?? "";
const APP_STORE_URL =
  process.env.NEXT_PUBLIC_APP_STORE_URL ??
  (APP_STORE_ID ? `https://apps.apple.com/app/id${APP_STORE_ID}` : "https://apps.apple.com");

export {
  SITE_BASE_URL,
  APP_NAME,
  APP_SCHEME,
  ANDROID_PACKAGE,
  PLAY_STORE_URL,
  APP_STORE_ID,
  APP_STORE_URL,
};

export function buildAppLinkMetadata(deepLink: string, canonicalUrl: string) {
  const metadata: Record<string, string> = {
    "al:ios:url": deepLink,
    "al:ios:app_name": APP_NAME,
    "al:android:url": deepLink,
    "al:android:package": ANDROID_PACKAGE,
    "al:android:app_name": APP_NAME,
    "al:android:play_store_url": PLAY_STORE_URL,
    "al:web:url": canonicalUrl,
  };

  if (APP_STORE_URL) {
    metadata["al:ios:app_store_url"] = APP_STORE_URL;
  }

  if (APP_STORE_ID) {
    metadata["al:ios:app_store_id"] = APP_STORE_ID;
    metadata["apple-itunes-app"] = `app-id=${APP_STORE_ID}, app-argument=${deepLink}`;
  }

  return metadata;
}
