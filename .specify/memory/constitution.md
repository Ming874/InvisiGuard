# [PROJECT_NAME] Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### I. 架構（Architecture）
邊界清晰、耦合最小、資料流顯式。偏好小而可組合、單一職責的模組。公開 API 穩定且具備文件。

### II. 命名（Naming）
命名精準且能揭示意圖；避免縮寫；除非極小型迴圈，不使用單字母識別符。函式與類別應傳達領域概念。

### III. 結構（Structure）
檔案短小且聚焦；依功能／領域分組；避免「上帝類別」；立即刪除死碼。

### IV. 可讀性（Readability）
統一使用自動格式化；嚴格的靜態檢查器強制風格。避免隱性副作用；可行處優先使用純函式。

### V. 註解與文件（Comments & Docs）
註解解釋「為什麼」，而非「做什麼」。模組層級文件描述目的、輸入／輸出、假設與範例。維持 README 與功能文件的最新性。

### VI. 錯誤處理（Error Handling）
錯誤訊息清楚且對使用者有意義；對程式員錯誤快速失敗；對操作性錯誤優雅復原；不得靜默吞掉例外。

### VII. 測試（Tests）
單元測試涵蓋率 ≥ 85%，測試可讀且具決定性。為關鍵路徑加入整合測試。測試命名／結構鏡射生產碼。偏好 Given／When／Then 的表格驅動案例。

### VIII. 效能與可及性（Performance & Accessibility）
維持效能預算（p95 延遲目標）且不犧牲可讀性；UI 遵循 WCAG AA，支援鍵盤優先流程。

### IX. 安全衛生（Security Hygiene）
驗證輸入、編碼輸出；程式碼中不保存機密；採用最小權限；對敏感操作記錄稽核日誌。

### X. 審查與 PR（Reviews & PRs）
PR 小而連貫，包含上下文與檢查清單；需綠燈 CI（lint、format、tests）與至少一位審核者；審核重點是可讀性與簡潔性。

### XI. 相依管理（Dependencies）
優先標準庫與經審核套件；版本固定；移除未使用依賴；對非平凡選擇撰寫理由。

### XII. 可觀測性（Observability）
結構化日誌且有明確識別；關鍵操作具量測；為重要流程加上追蹤以助除錯。

### XIII. 交付（Delivery）
以 trunk 為主、短生命週期分支；風險變更以功能旗標控管；文件化回滾計畫。每個功能皆附規格、計劃、任務與驗收標準。

### XIV. 持續改善（Continuous Improvement）
定期為提升清晰度而重構；遵守「童軍守則」（讓程式更乾淨）；以明確負責人與時間表追蹤技術債。

## [SECTION_2_NAME]
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->

[SECTION_2_CONTENT]
<!-- Example: Technology stack requirements, compliance standards, deployment policies, etc. -->

## [SECTION_3_NAME]
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

[SECTION_3_CONTENT]
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
- 本憲章優先於其他開發約定；任何修訂需文件化、獲得批准並提供遷移計畫。
- 所有 PR／評審需驗證對本憲章之遵循；複雜度須有正當理由並附權衡記錄。
- 於日常開發請參照開發指引文件以保持一致性與可讀性。

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
