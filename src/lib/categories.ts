import type { TFunction } from "i18next";

const CATEGORY_TRANSLATION_KEYS: Record<string, string> = {
  "Open Geo Stack": "categories.openGeoStack",
  "Mapping & Cartography": "categories.mappingCartography",
  "Standards & Data Infra": "categories.standardsDataInfra",
  "AI & Automation": "categories.aiAutomation",
  "EO / 3D / Survey": "categories.eo3dSurvey",
  "Community & Programs": "categories.communityPrograms",
  "Domain Signals": "categories.domainSignals",
  "Other keywords": "categories.otherKeywords",
  "Desktop GIS": "categories.desktopGis",
  "Web Mapping": "categories.webMapping",
  "Server & APIs": "categories.serverApis",
  "Database & Storage": "categories.databaseStorage",
  "Geo Data Processing": "categories.geoDataProcessing",
  "3D & EO Platforms": "categories.eoPlatforms",
  "Other Libraries": "categories.otherLibraries",
  "Generative & Language AI": "categories.genaiLanguage",
  "Machine Learning & Prediction": "categories.mlPrediction",
  "Vision & Detection": "categories.visionDetection",
  "Graph & Neural Models": "categories.graphNeural",
  "GeoAI & Agents": "categories.geoaiAgents",
  "AI Tooling": "categories.aiTooling",
  "General AI Signals": "categories.generalAiSignals",
  "Other AI Signals": "categories.otherAiSignals",
  "Cloud Platforms & Architecture": "categories.cloudPlatformsArchitecture",
  "Cloud Storage & Delivery": "categories.cloudStorageDelivery",
  "Orchestration & Operations": "categories.orchestrationOperations",
  "Runtime & Scalable Processing": "categories.runtimeScalableProcessing",
  "Cloud Tooling": "categories.cloudTooling",
  "Other Cloud Signals": "categories.otherCloudSignals",
  "3D Models & Twins": "categories.threeDModelsTwins",
  "Point Clouds & Reconstruction": "categories.pointCloudsReconstruction",
  "Web Rendering & Streaming": "categories.webRenderingStreaming",
  "3D Platforms & Standards": "categories.threeDPlatformsStandards",
  "General 3D Signals": "categories.general3dSignals",
};

// 데이터 카테고리 라벨은 번역 키가 있을 때만 치환한다.
export function translateCategory(t: TFunction, category: string) {
  const key = CATEGORY_TRANSLATION_KEYS[category];
  return key ? t(key) : category;
}
