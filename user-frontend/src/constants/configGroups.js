export const CONFIG_GROUPS = {
  'LLM 模型': [
    ['INSIGHT_ENGINE_MODEL_NAME', 'Insight 模型', false],
    ['INSIGHT_ENGINE_MODEL_PROVIDER', 'Insight Provider', false],
    ['MEDIA_ENGINE_MODEL_NAME', 'Media 模型', false],
    ['MEDIA_ENGINE_MODEL_PROVIDER', 'Media Provider', false],
    ['REPORT_ENGINE_MODEL_NAME', 'Report 模型', false],
    ['REPORT_ENGINE_MODEL_PROVIDER', 'Report Provider', false],
    ['HOST_MODEL_NAME', 'Host 模型', false],
    ['HOST_MODEL_PROVIDER', 'Host Provider', false],
  ],
  'API 密钥': [
    ['INSIGHT_ENGINE_API_KEY', 'Insight API Key', true],
    ['INSIGHT_ENGINE_BASE_URL', 'Insight Base URL', false],
    ['MEDIA_ENGINE_API_KEY', 'Media API Key', true],
    ['MEDIA_ENGINE_BASE_URL', 'Media Base URL', false],
    ['REPORT_ENGINE_API_KEY', 'Report API Key', true],
    ['REPORT_ENGINE_BASE_URL', 'Report Base URL', false],
    ['HOST_API_KEY', 'Host API Key', true],
    ['HOST_BASE_URL', 'Host Base URL', false],
  ],
  '搜索工具': [
    ['ANSPIRE_API_KEY', 'Anspire API Key', true],
    ['ANSPIRE_BASE_URL', 'Anspire Base URL', false],
  ],
  '数据库': [
    ['DB_HOST', '数据库主机', false],
    ['DB_PORT', '数据库端口', false],
    ['DB_NAME', '数据库名称', false],
    ['DB_USER', '数据库用户', false],
  ],
}
