import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import { resources } from "@/i18n/resources";

const STORAGE_KEY = "foss4g-dashboard-language";
const supportedLanguages = ["en", "ko", "ja"] as const;

function detectInitialLanguage() {
  if (typeof window === "undefined") {
    return "en";
  }

  const saved = window.localStorage.getItem(STORAGE_KEY);
  if (saved && supportedLanguages.includes(saved as (typeof supportedLanguages)[number])) {
    return saved;
  }

  return "en";
}

if (!i18n.isInitialized) {
  i18n.use(initReactI18next).init({
    resources,
    lng: detectInitialLanguage(),
    fallbackLng: "en",
    supportedLngs: [...supportedLanguages],
    interpolation: {
      escapeValue: false,
    },
  });

  if (typeof window !== "undefined") {
    window.document.documentElement.lang = i18n.language;
  }

  i18n.on("languageChanged", (language) => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, language);
      window.document.documentElement.lang = language;
    }
  });
}

export default i18n;
