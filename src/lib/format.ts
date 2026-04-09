import { useMemo } from "react";
import { useTranslation } from "react-i18next";

export const supportedLanguages = ["en", "ko", "ja"] as const;

export type SupportedLanguage = (typeof supportedLanguages)[number];

// 브라우저와 i18n 설정 전반에서 동일한 언어 코드를 사용한다.
export function normalizeLanguage(language?: string): SupportedLanguage {
  if (!language) {
    return "en";
  }

  const matchedLanguage = supportedLanguages.find((code) => language.startsWith(code));
  return matchedLanguage ?? "en";
}

// 현재 선택된 언어에 맞는 숫자 포맷터를 한 곳에서 만든다.
export function useLocaleFormatters() {
  const { i18n } = useTranslation();
  const language = normalizeLanguage(i18n.resolvedLanguage ?? i18n.language);

  return useMemo(
    () => ({
      language,
      number: new Intl.NumberFormat(language),
      percent: new Intl.NumberFormat(language, {
        style: "percent",
        maximumFractionDigits: 1,
      }),
    }),
    [language],
  );
}
