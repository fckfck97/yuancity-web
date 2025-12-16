'use client';

import { useCallback, useEffect, useRef } from "react";

type DeepLinkLauncherProps = {
  deepLink: string;
  appStoreUrl: string;
  playStoreUrl: string;
  autolaunch?: boolean;
  label?: string;
};

function detectOS() {
  if (typeof navigator === "undefined") {
    return { isIOS: false, isAndroid: false };
  }
  const ua = navigator.userAgent || "";
  return {
    isIOS: /iP(hone|od|ad)/.test(ua),
    isAndroid: /Android/i.test(ua),
  };
}

export default function DeepLinkLauncher({
  deepLink,
  appStoreUrl,
  playStoreUrl,
  autolaunch = false,
  label = "Abrir en GreenCloset",
}: DeepLinkLauncherProps) {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cancelRef = useRef<(() => void) | null>(null);

  const clearTimer = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  const tryOpen = useCallback(() => {
    if (typeof window === "undefined" || typeof document === "undefined") return;

    if (cancelRef.current) {
      cancelRef.current();
    }

    const { isIOS, isAndroid } = detectOS();

    const cancel = () => {
      clearTimer();
      document.removeEventListener("visibilitychange", handleVisibility);
      window.removeEventListener("pagehide", cancel);
      window.removeEventListener("blur", cancel);
      cancelRef.current = null;
    };

    function handleVisibility() {
      if (document.visibilityState === "hidden") {
        cancel();
      }
    }

    document.addEventListener("visibilitychange", handleVisibility);
    window.addEventListener("pagehide", cancel);
    window.addEventListener("blur", cancel);
    cancelRef.current = cancel;

    window.location.href = deepLink;

    timeoutRef.current = window.setTimeout(() => {
      if (isIOS && appStoreUrl) {
        window.location.href = appStoreUrl;
      } else if (isAndroid && playStoreUrl) {
        window.location.href = playStoreUrl;
      }
      cancel();
    }, 1000);
  }, [appStoreUrl, clearTimer, deepLink, playStoreUrl]);

  useEffect(() => {
    if (autolaunch) {
      tryOpen();
    }
    return () => {
      if (cancelRef.current) {
        cancelRef.current();
      } else {
        clearTimer();
      }
    };
  }, [autolaunch, clearTimer, tryOpen]);

  return (
    <button
      type="button"
      onClick={tryOpen}
      className="w-full rounded-2xl bg-gradient-to-r from-emerald-500 to-lime-500 px-6 py-4 text-lg font-semibold text-white shadow-lg transition-transform hover:scale-[1.01] focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-300"
    >
      {label}
    </button>
  );
}
