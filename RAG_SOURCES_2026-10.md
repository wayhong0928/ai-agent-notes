# RAG 系列來源庫（2026-10）

這份檔案是之後撰寫 RAG 系列網頁的來源庫，不是網頁內容，也不會被 `build.py` 建置（檔案放在 repo 根目錄，不在 `docs/`）。

- 擷取與核對日期：2026-10-23
- 收錄原則：官方文件、原始論文、主要框架或研究機構的官方部落格優先；不收行銷文與內容農場。廠商文件只收產品說明文件或具名作者的技術報告，不收落地頁。
- 引文規則：每筆「引文」都是英文原文逐字照抄。網頁來源是實際抓下全文後，用腳本把引文跟頁面文字比對（只正規化空白、彎引號與 PDF 斷行的連字號）；arXiv 論文是跟 arXiv 官方 API 回傳的摘要逐字比對。抓不到原文的標「**未核對全文**」。
- 「主張」欄是整理者用自己的話摘要，不是翻譯。arXiv 論文的主張只根據摘要，沒讀全文的實驗細節。
- 日期：arXiv 寫第一版送出日；官方文件頁沒有標日期的，寫「未標日期」。

**篇號對照**（詳見第 4 節）：R01 基本流程｜R02 切塊｜R03 Embedding｜R04 向量資料庫｜R05 Hybrid search｜R06 Reranking｜R07 Contextual Retrieval｜R08 GraphRAG｜R09 Agentic RAG｜R10 評估｜R11 長上下文取捨｜R12 失敗模式與 prompt injection

---

## 1. 站內已經談過的段落（之後避免重複）

盤點範圍：`README.md`、`README.en.md`、`docs/*.md`、`reports/*.md`。站內**沒有**任何一頁正式講 RAG 流程、embedding 模型、向量資料庫或 reranking；以下是零星提到的地方。

### RAG

| 位置 | 內容 | 系列處理方式 |
|---|---|---|
| `docs/projects.md:26` | Claude Projects 知識庫接近 context 上限時自動切換 RAG 模式，「expand capacity by up to 10x」，只限付費方案 | R01 舉「產品裡的 RAG」例子時直接連過去，不再重講方案差異 |
| `docs/projects.md:47`、`:87`、`:88` | 方案表與比較表裡的 RAG 擴充列；`:88` 指出 RAG 模式是「擴充容量」，不是「只依上傳內容回答」 | `:88` 這個區分正好可以接 R12 的「檢索到了不等於答對」 |
| `docs/projects.md:112` | 來源 S1（support.claude.com Projects 文章） | 不重複收錄 |
| `docs/paid-tier.md:16`、`:52` | 同一件事（Projects 的 RAG 擴充）的方案表更正紀錄 | 不重講 |
| `docs/free-tier.md:17`、`:48`、`:90` | 同上，Free 沒有 RAG 擴充 | 不重講 |
| `docs/tools-catalog.md:154` | 第三方教學 repo `amitshekhariitbhu/ai-system-design`，提到 RAG、向量資料庫、Embedding Cache、Semantic Cache | 只是工具目錄條目，不是本系列來源（作者會導流自家課程，不符合收錄原則） |

### Embedding、向量資料庫

站內只有 `docs/tools-catalog.md:154` 那一條順帶提到「向量資料庫」與「Embedding Cache」，沒有任何正文。R03、R04 可以從零寫。

### Context engineering 與上下文管理

| 位置 | 內容 | 系列處理方式 |
|---|---|---|
| `docs/agent-basics.md:30-38`（第二節） | 上下文視窗為什麼會滿、context rot、壓縮與新開對話的差別 | R11 講長上下文的衰退時連過去，只補論文層級的證據（Lost in the Middle、RULER、Chroma Context Rot），不重講 Claude Code 的壓縮行為 |
| `docs/agent-basics.md:171` | 參考資料 [3]：Effective context engineering for AI agents | 同一篇在本來源庫 R09-6 再收一次，但引的是「just in time」檢索那段，不是 context rot 那段 |
| `docs/tools-catalog.md:28` | 同一篇文章的一句話摘要（上下文是有限資源、邊際報酬遞減） | 不重複摘要 |
| `docs/harness.md:9` | harness 是「提供工具並管理模型看到的上下文」的那一層 | R09 談 agentic RAG 時連過去 |
| `docs/harness.md:26` | 官方來源表裡的 Effective context engineering 一列 | 不重複 |
| `docs/harness.md:45-47`（2.4 節） | 讓子代理去探索、不污染主線對話 | R09 談「多代理平行檢索」時連過去 |
| `docs/subagent.md:9`、`:56`、`:61`、`:218` | subagent 把搜尋結果留在自己的 context，只回傳摘要 | 同上 |
| `docs/extensions.md:22-25` | CLAUDE.md 全程常駐、SKILL 隨需載入、Subagent 獨立上下文 | R09 可用來對照「預先載入 vs. 即時檢索」，不重講機制 |
| `docs/skill-build.md:36`、`:231`、`:323` | SKILL 的 progressive disclosure（只先讀 name／description，需要時才展開） | R09 可以點出這是「即時檢索」的一種形式，連過去即可 |
| `docs/session-handoff.md:5`、`:92` | 上下文會滿、SessionStart 注入的內容也佔上下文 | 與 RAG 關係弱，不需引用 |

### Prompt injection、檢索到了不等於答對

| 位置 | 內容 | 系列處理方式 |
|---|---|---|
| `docs/mcp.md:138` | 官方警告「Servers that fetch external content can expose you to prompt injection risk.」 | R12 直接連過去，不重抄 |
| `docs/mcp.md:140-142` | Claude Code security 頁的 MCP 安全段與五點處理不信任內容的建議 | R12 連過去；本來源庫 R12-10 收的是同一頁的「Protect against prompt injection」定義段 |
| `docs/mcp.md:147` | 整理者歸納的 MCP server 審查判準（會爬外部內容＝高風險注入來源） | R12 連過去 |
| `docs/mcp.md:87`、`:133-134`、`docs/extensions.md:155` | 「MCP 只解決有沒有東西可以查，不保證不答錯」 | R12 失敗模式的引子，連過去即可 |

### 知識圖譜

`docs/tools-catalog.md:105-112`（「程式碼庫知識圖譜」小節）收了 Graphify、Understand-Anything 兩個把專案轉成知識圖譜的工具。R08 講 GraphRAG 時可以連過去當實作例子，但要講清楚這兩個工具不是 Microsoft GraphRAG。

### 順帶發現（未修改，僅記錄）

- 站內 `docs/agent-basics.md:171`、`docs/harness.md:26`、`docs/tools-catalog.md:28` 用的網址 `www.anthropic.com/engineering/effective-context-engineering-for-ai-agents`，2026-10-23 實測會轉址到 `www.anthropic.com/research/effective-context-engineering-for-ai-agents`，連結仍可用。Contextual Retrieval 的 `/news/contextual-retrieval` 也轉到 `/research/contextual-retrieval`。
- 幾個框架文件網域搬家了：LangChain 文件現在在 `docs.langchain.com`，LlamaIndex 在 `developers.llamaindex.ai`，Chroma 研究報告在 `www.trychroma.com/research/`，Ragas 文件頁的 repo 標示改為 `vibrantlabsai/ragas`。下面的網址都是搬家後的實際位置。

---

## 2. 來源清單

### R01　RAG 基本流程與原始論文

**R01-1　Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks**
- 作者／機構：Patrick Lewis、Ethan Perez、Aleksandra Piktus 等 12 人（Facebook AI Research、UCL、NYU）
- 日期：2020-05-22（arXiv v1；NeurIPS 2020）
- 網址：<https://arxiv.org/abs/2005.11401>
- 主張：「RAG」這個名詞的出處。把預訓練 seq2seq 模型（參數記憶）跟 Wikipedia 的稠密向量索引（非參數記憶）接起來一起微調，在開放領域問答拿到最佳成績，生成內容也比純參數模型更具體、更符合事實。
- 引文：「We introduce RAG models where the parametric memory is a pre-trained seq2seq model and the non-parametric memory is a dense vector index of Wikipedia, accessed with a pre-trained neural retriever.」
- 核對：arXiv 摘要逐字比對
- 適合：R01（定義與歷史）

**R01-2　REALM: Retrieval-Augmented Language Model Pre-Training**
- 作者／機構：Kelvin Guu、Kenton Lee、Zora Tung 等 5 人（Google Research）
- 日期：2020-02-10（arXiv v1）
- 網址：<https://arxiv.org/abs/2002.08909>
- 主張：比 Lewis 等人早三個月，把「檢索器」放進語言模型預訓練階段，讓知識以可檢查的文件形式存在，而不是全部藏在參數裡。適合用來說明 RAG 不是憑空出現的單一發明。
- 引文：「However, this knowledge is stored implicitly in the parameters of a neural network, requiring ever-larger networks to cover more facts.」
- 核對：arXiv 摘要逐字比對
- 適合：R01（為什麼需要外部記憶）

**R01-3　Retrieval-Augmented Generation for Large Language Models: A Survey**
- 作者／機構：Yunfan Gao、Yun Xiong、Xinyu Gao 等 10 人（同濟大學、復旦大學）
- 日期：2023-12-18（arXiv v1；目前 v5）
- 網址：<https://arxiv.org/abs/2312.10997>
- 主張：把 RAG 演進分成 Naive、Advanced、Modular 三代，並拆成檢索、生成、增強三個元件來整理技術。系列的總架構可以參考這個分法。
- 引文：「This comprehensive review paper offers a detailed examination of the progression of RAG paradigms, encompassing the Naive RAG, the Advanced RAG, and the Modular RAG.」
- 核對：arXiv 摘要逐字比對
- 適合：R01（全系列地圖）

**R01-4　Introduction to RAG（LlamaIndex 官方文件）**
- 作者／機構：LlamaIndex
- 日期：未標日期
- 網址：<https://developers.llamaindex.ai/python/framework/understanding/rag/>
- 主張：框架角度的 RAG 流程：載入、索引、儲存、查詢、評估五個階段。適合給讀者一張「實作時會碰到哪些步驟」的清單。
- 引文：「There are five key stages within RAG, which in turn will be a part of most larger applications you build.」
- 核對：網頁全文比對
- 適合：R01（流程圖）

**R01-5　Retrieval（LangChain 官方文件）**
- 作者／機構：LangChain
- 日期：未標日期
- 網址：<https://docs.langchain.com/oss/python/deepagents/retrieval>（原 `langchain/retrieval` 轉址至此）
- 主張：用「LLM 的 context 有限、知識是靜態的」解釋為什麼要檢索，並把 RAG 架構分成 2-step、Agentic、Hybrid 三型。三型分類可以直接當 R01 結尾、R09 開頭的橋。
- 引文：「Retrieval addresses these problems by fetching relevant external knowledge at query time.」
- 核對：網頁全文比對
- 適合：R01、R09

### R02　Chunking 策略

**R02-1　Evaluating Chunking Strategies for Retrieval（Chroma 技術報告）**
- 作者／機構：Brandon Smith、Anton Troynikov（Chroma）
- 日期：2024-07-03
- 網址：<https://www.trychroma.com/research/evaluating-chunking>
- 主張：用 token 層級的 precision／recall／IoU 評估常見切塊法，發現切法不同 recall 可差到 9%，而且某些熱門切塊器的預設參數表現偏差。
- 引文：「Notably, we find that default settings for certain popular chunking strategies can lead to relatively poor performance.」
- 核對：網頁全文比對
- 適合：R02（主要實證）

**R02-2　Is Semantic Chunking Worth the Computational Cost?**
- 作者／機構：Renyi Qu、Ruixuan Tu、Forrest Bao（Vectara）
- 日期：2024-10-16（arXiv v1）
- 網址：<https://arxiv.org/abs/2410.13070>
- 主張：在文件檢索、證據檢索、問答生成三種任務上比較語意切塊與固定長度切塊，結論是語意切塊多花的計算成本換不到穩定的效果提升。
- 引文：「The results show that the computational costs associated with semantic chunking are not justified by consistent performance gains.」
- 核對：arXiv 摘要逐字比對
- 適合：R02（反方證據，見第 3 節衝突 2）

**R02-3　Dense X Retrieval: What Retrieval Granularity Should We Use?**
- 作者／機構：Tong Chen、Hongwei Wang、Sihao Chen 等 8 人
- 日期：2023-12-11（arXiv v1）
- 網址：<https://arxiv.org/abs/2312.06648>
- 主張：檢索單位（文件、段落、句子）是常被忽略的設計選擇；提出以「命題」（proposition，一句話一個事實）為單位建索引，檢索效果優於段落。
- 引文：「We discover that the retrieval unit choice significantly impacts the performance of both retrieval and downstream tasks.」
- 核對：arXiv 摘要逐字比對
- 適合：R02（切多細）

**R02-4　Text splitter integrations（LangChain 官方文件）**
- 作者／機構：LangChain
- 日期：未標日期
- 網址：<https://docs.langchain.com/oss/python/integrations/splitters>
- 主張：把切塊器分成依文字結構、依長度、依文件結構三類；官方建議多數情況先用 `RecursiveCharacterTextSplitter`。
- 引文：「For most use cases, start with the RecursiveCharacterTextSplitter .」（原文類別名稱與句點之間有空格，照抄）
- 核對：網頁全文比對
- 適合：R02（實作預設值）

**R02-5　Node Parser Modules：SemanticSplitterNodeParser（LlamaIndex 官方文件）**
- 作者／機構：LlamaIndex
- 日期：未標日期
- 網址：<https://developers.llamaindex.ai/python/framework/module_guides/loading/node_parsers/modules/>
- 主張：說明語意切塊的做法：不用固定長度，而是用相鄰句子的 embedding 相似度決定斷點；文件同時註明這個概念來自 Greg Kamradt 的教學影片，且斷點門檻需要調。
- 引文：「Instead of chunking text with a fixed chunk size, the semantic splitter adaptively picks the breakpoint in-between sentences using embedding similarity.」
- 核對：網頁全文比對
- 適合：R02（語意切塊的正方說明，對照 R02-2）

**R02-6　Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models**
- 作者／機構：Michael Günther、Isabelle Mohr、Daniel James Williams 等 5 人（Jina AI）
- 日期：2024-09-07（arXiv v1）
- 網址：<https://arxiv.org/abs/2409.04701>
- 主張：先把整份長文件丟進長上下文 embedding 模型，在 pooling 前才切塊，讓每塊的向量保有全文脈絡；不需額外訓練。是 Contextual Retrieval 之外另一條「讓 chunk 帶脈絡」的路。
- 引文：「However, chunk embeddings created in this way can lose contextual information from surrounding chunks, resulting in sub-optimal representations.」
- 核對：arXiv 摘要逐字比對
- 適合：R02、R07（對照組）

### R03　Embedding 模型與評測（MTEB）

**R03-1　MTEB: Massive Text Embedding Benchmark**
- 作者／機構：Niklas Muennighoff、Nouamane Tazi、Loïc Magne、Nils Reimers（Hugging Face、Cohere）
- 日期：2022-10-13（arXiv v1）
- 網址：<https://arxiv.org/abs/2210.07316>
- 主張：8 類任務、58 個資料集、112 種語言的 embedding 評測基準；評了 33 個模型後發現沒有一種方法在所有任務都最好。
- 引文：「We find that no particular text embedding method dominates across all tasks.」
- 核對：arXiv 摘要逐字比對
- 適合：R03（怎麼讀排行榜）

**R03-2　MMTEB: Massive Multilingual Text Embedding Benchmark**
- 作者／機構：Kenneth Enevoldsen、Isaac Chung、Imene Kerboua 等 86 人（社群協作）
- 日期：2025-02-19（arXiv v1）
- 網址：<https://arxiv.org/abs/2502.13595>
- 主張：MTEB 的多語擴充版，500 多個任務、250 多種語言；發現數十億參數的 LLM 型 embedding 不一定最好，公開模型第一名只有 5.6 億參數。對中文讀者選模型有直接參考價值。
- 引文：「We find that while large language models (LLMs) with billions of parameters can achieve state-of-the-art performance on certain language subsets and task categories, the best-performing publicly available model is multilingual-e5-large-instruct with only 560 million parameters.」
- 核對：arXiv 摘要逐字比對
- 適合：R03（模型大小不等於排名）

**R03-3　MTEB: Massive Text Embedding Benchmark（Hugging Face 部落格）**
- 作者／機構：Niklas Muennighoff（Hugging Face）
- 日期：2022-10-19
- 網址：<https://huggingface.co/blog/mteb>
- 主張：MTEB 官方介紹文，說明排行榜、論文、GitHub 三者的分工。排行榜本身（`huggingface.co/spaces/mteb/leaderboard`）是動態網頁，抓不到可引用的文字，所以引這篇。
- 引文：「The 🥇 leaderboard provides a holistic view of the best text embedding models out there on a variety of tasks.」
- 核對：網頁全文比對
- 適合：R03

**R03-4　Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks**
- 作者／機構：Nils Reimers、Iryna Gurevych（UKP Lab，TU Darmstadt）
- 日期：2019-08-27（arXiv v1；EMNLP 2019）
- 網址：<https://arxiv.org/abs/1908.10084>
- 主張：BERT 原本要把兩句一起輸入才能比相似度，找最相似的一對要 65 小時；改成雙塔各自編碼成向量後用餘弦相似度比，降到 5 秒。這是「為什麼要先把文件變成向量」最好懂的例子。
- 引文：「This reduces the effort for finding the most similar pair from 65 hours with BERT / RoBERTa to about 5 seconds with SBERT, while maintaining the accuracy from BERT.」
- 核對：arXiv 摘要逐字比對
- 適合：R03（bi-encoder 原理）、R06（對照 cross-encoder）

**R03-5　Dense Passage Retrieval for Open-Domain Question Answering**
- 作者／機構：Vladimir Karpukhin、Barlas Oğuz、Sewon Min 等 8 人（Facebook AI）
- 日期：2020-04-10（arXiv v1；EMNLP 2020）
- 網址：<https://arxiv.org/abs/2004.04906>
- 主張：只用稠密向量的雙編碼器檢索，在開放領域問答的 top-20 準確率比 Lucene-BM25 高 9 到 19 個百分點。RAG 原始論文的檢索器就是 DPR。
- 引文：「When evaluated on a wide range of open-domain QA datasets, our dense retriever outperforms a strong Lucene-BM25 system largely by 9%-19% absolute in terms of top-20 passage retrieval accuracy, and helps our end-to-end QA system establish new state-of-the-art on multiple open-domain QA benchmarks.」
- 核對：arXiv 摘要逐字比對
- 適合：R03、R05（見第 3 節衝突 3）

**R03-6　Vector embeddings（OpenAI 官方文件）**
- 作者／機構：OpenAI
- 日期：未標日期
- 網址：<https://developers.openai.com/api/docs/guides/embeddings>（原 `platform.openai.com/docs/guides/embeddings` 轉址至此）
- 主張：用一句話定義 embedding：向量之間的距離代表文字的相關程度，並列出搜尋、分群、推薦等用途。適合當 R03 開場定義。
- 引文：「The distance between two vectors measures their relatedness.」
- 核對：網頁全文比對
- 適合：R03（定義）

**R03-7　Embeddings（Claude 官方文件）**
- 作者／機構：Anthropic
- 日期：未標日期
- 網址：<https://platform.claude.com/docs/en/build-with-claude/embeddings>（原 `docs.claude.com` 轉址至此）
- 主張：Anthropic 不提供自家 embedding 模型，文件以 Voyage AI 為例，但明說應該比較多家供應商。本站讀者多用 Claude，這點要講清楚。
- 引文：「Anthropic does not offer its own embedding model.」
- 核對：網頁全文比對
- 適合：R03、R07

### R04　向量資料庫與近似最近鄰（ANN）

**R04-1　Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs**
- 作者／機構：Yu. A. Malkov、D. A. Yashunin
- 日期：2016-03-30（arXiv v1；IEEE TPAMI 2018）
- 網址：<https://arxiv.org/abs/1603.09320>
- 主張：HNSW 原始論文。多層鄰近圖，從最上層開始找，搜尋複雜度接近對數；這是 pgvector、Qdrant、Weaviate 等主流向量庫的預設索引。
- 引文：「Starting search from the upper layer together with utilizing the scale separation boosts the performance compared to NSW and allows a logarithmic complexity scaling.」
- 核對：arXiv 摘要逐字比對
- 適合：R04（HNSW 怎麼運作）

**R04-2　The Faiss library**
- 作者／機構：Matthijs Douze、Alexandr Guzhva、Chengqi Deng 等 9 人（Meta FAIR）
- 日期：2024-01-16（arXiv v1）
- 網址：<https://arxiv.org/abs/2401.08281>
- 主張：Faiss 的設計說明，把向量搜尋描述成一個取捨空間（速度、記憶體、準確度），並定位 Faiss 是向量資料庫的核心功能元件，而不是資料庫本身。
- 引文：「The Faiss library is dedicated to vector similarity search, a core functionality of vector databases.」
- 核對：arXiv 摘要逐字比對
- 適合：R04（向量庫 vs. 向量搜尋函式庫）

**R04-3　Billion-scale similarity search with GPUs**
- 作者／機構：Jeff Johnson、Matthijs Douze、Hervé Jégou（Facebook AI Research）
- 日期：2017-02-28（arXiv v1）
- 網址：<https://arxiv.org/abs/1702.08734>
- 主張：Faiss GPU 版的原始論文，用乘積量化（product quantization）做壓縮域搜尋，4 張 GPU 不到 12 小時建好 10 億向量的 k-NN 圖。適合講「量化」為什麼能省記憶體。
- 引文：「We apply it in different similarity search scenarios, by proposing optimized design for brute-force, approximate and compressed-domain search based on product quantization.」
- 核對：arXiv 摘要逐字比對
- 適合：R04（量化）

**R04-4　ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms**
- 作者／機構：Martin Aumüller、Erik Bernhardsson、Alexander Faithfull
- 日期：2018-07-15（arXiv v1）
- 網址：<https://arxiv.org/abs/1807.05614>；即時結果 <http://ann-benchmarks.com/>
- 主張：ANN 演算法的標準評測工具；結論之一是做法差很多的演算法，在品質與效能的取捨上可以很接近，所以選型不能只看名氣。
- 引文：「Interestingly, very different approaches to $k$-NN search yield comparable quality-performance trade-offs.」（摘要原文含 LaTeX 記號，照抄）
- 核對：arXiv 摘要逐字比對
- 適合：R04（怎麼比較向量庫）

**R04-5　pgvector README**
- 作者／機構：pgvector 專案（Andrew Kane 維護）
- 日期：未標日期（README 現行版，2026-10-23 擷取）
- 網址：<https://github.com/pgvector/pgvector>
- 主張：PostgreSQL 的向量擴充；預設是精確搜尋，加了 HNSW 或 IVFFlat 索引才變成近似搜尋，用一點 recall 換速度，而且加索引後同一查詢的結果會變。這句是向讀者解釋「近似」代價最直白的官方說法。
- 引文：「You can add an index to use approximate nearest neighbor search, which trades some recall for speed.」
- 核對：網頁全文比對（透過 raw.githubusercontent.com 抓 README）
- 適合：R04（實作入門，已有 Postgres 的人不一定要另裝向量庫）

### R05　Hybrid search 與 BM25

**R05-1　The Probabilistic Relevance Framework: BM25 and Beyond**
- 作者／機構：Stephen Robertson、Hugo Zaragoza（Microsoft Research 等）
- 日期：2009（Foundations and Trends in Information Retrieval, Vol. 3, No. 4）
- 網址：<https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf>（DOI 10.1561/1500000019）
- 主張：BM25 原作者之一寫的完整回顧，交代 BM25 的機率檢索理論來源（1970–80 年代的研究）與 BM25F 等延伸。
- 引文：「The Probabilistic Relevance Framework (PRF) is a formal framework for document retrieval, grounded in work done in the 1970–1980s, which led to the development of one of the most successful text-retrieval algorithms, BM25.」
- 核對：PDF 全文比對
- 適合：R05（BM25 從哪來）

**R05-2　Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods**
- 作者／機構：Gordon V. Cormack、Charles L. A. Clarke、Stefan Büttcher（University of Waterloo、Google）
- 日期：2009（SIGIR 2009）
- 網址：<https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf>（原 `plg.uwaterloo.ca` 網址轉址至此）
- 主張：RRF 的原始論文。只用名次倒數相加就能融合多個檢索系統的結果，表現勝過任一單一系統。今天多數向量庫的 hybrid search 都用這個公式。
- 引文：「Reciprocal Rank Fusion (RRF), a simple method for combining the document rankings from multiple IR systems, consistently yields better results than any individual system, and better results than the standard method Condorcet Fuse.」
- 核對：PDF 全文比對
- 適合：R05（融合）

**R05-3　BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models**
- 作者／機構：Nandan Thakur、Nils Reimers、Andreas Rücklé 等 5 人（UKP Lab，TU Darmstadt）
- 日期：2021-04-17（arXiv v1；NeurIPS 2021 Datasets and Benchmarks）
- 網址：<https://arxiv.org/abs/2104.08663>
- 主張：18 個資料集的零樣本檢索評測；BM25 是很穩的基準線，稠密檢索換到沒訓練過的領域常常輸給它。這是「為什麼還要留 BM25」的主要證據。
- 引文：「Our results show BM25 is a robust baseline and re-ranking and late-interaction-based models on average achieve the best zero-shot performances, however, at high computational costs.」
- 核對：arXiv 摘要逐字比對
- 適合：R05、R06（見第 3 節衝突 3）

**R05-4　Reciprocal rank fusion（Elasticsearch 官方文件）**
- 作者／機構：Elastic
- 日期：未標日期
- 網址：<https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion>
- 主張：Elasticsearch 的 RRF retriever 說明，強調 RRF 不需要調參、也不要求各路分數彼此可比。
- 引文：「RRF requires no tuning, and the different relevance indicators do not have to be related to each other to achieve high-quality results.」
- 核對：網頁全文比對
- 適合：R05

**R05-5　Hybrid search（Weaviate 官方文件，Concepts）**
- 作者／機構：Weaviate
- 日期：未標日期
- 網址：<https://docs.weaviate.io/weaviate/concepts/search/hybrid-search>
- 主張：Weaviate 的 hybrid search 平行跑向量搜尋與 BM25，再融合分數；提供 `relativeScoreFusion`（預設）與 `rankedFusion` 兩種，官方偏好保留原始分數資訊的前者。
- 引文：「The main reason is that relativeScoreFusion retains more information from the original searches than rankedFusion , which only retains the rankings.」（原文名稱與逗號間有空格，照抄）
- 核對：網頁全文比對
- 適合：R05（見第 3 節衝突 4）

**R05-6　Hybrid search overview（Pinecone 官方文件）**
- 作者／機構：Pinecone
- 日期：未標日期
- 網址：<https://docs.pinecone.io/guides/search/hybrid-search>
- 主張：產品文件角度的一句話定義：關鍵字訊號與語意訊號互補，各自漏掉的由另一邊補上。
- 引文：「Each method misses what the other catches, and hybrid search closes that gap.」
- 核對：網頁全文比對
- 適合：R05（開場定義）

### R06　Reranking

**R06-1　Passage Re-ranking with BERT**
- 作者／機構：Rodrigo Nogueira、Kyunghyun Cho（NYU）
- 日期：2019-01-13（arXiv v1）
- 網址：<https://arxiv.org/abs/1901.04085>
- 主張：把 BERT 當 cross-encoder 用在段落重排序，在 MS MARCO 上 MRR@10 相對提升 27%。現代 reranker 的起點。
- 引文：「In this paper, we describe a simple re-implementation of BERT for query-based passage re-ranking.」
- 核對：arXiv 摘要逐字比對
- 適合：R06（起源）

**R06-2　ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT**
- 作者／機構：Omar Khattab、Matei Zaharia（Stanford）
- 日期：2020-04-27（arXiv v1；SIGIR 2020）
- 網址：<https://arxiv.org/abs/2004.12832>
- 主張：cross-encoder 每對 query-文件都要過一次大模型，太貴；ColBERT 改成「後期互動」，文件表示可以預先算好，速度快兩個數量級、效果接近。用來說明 bi-encoder、cross-encoder 之間還有中間選項。
- 引文：「Results show that ColBERT's effectiveness is competitive with existing BERT-based models (and outperforms every non-BERT baseline), while executing two orders-of-magnitude faster and requiring four orders-of-magnitude fewer FLOPs per query.」
- 核對：arXiv 摘要逐字比對
- 適合：R06

**R06-3　Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents（RankGPT）**
- 作者／機構：Weiwei Sun、Lingyong Yan、Xinyu Ma 等 8 人（山東大學、百度）
- 日期：2023-04-19（arXiv v1；EMNLP 2023）
- 網址：<https://arxiv.org/abs/2304.09542>
- 主張：直接讓 LLM 做排序，在常見 IR 基準上可追平甚至超過有監督模型；再蒸餾成小模型降低成本。
- 引文：「Surprisingly, our experiments reveal that properly instructed LLMs can deliver competitive, even superior results to state-of-the-art supervised methods on popular IR benchmarks.」
- 核對：arXiv 摘要逐字比對
- 適合：R06（LLM 當 reranker）

**R06-4　Retrieve & Re-Rank（Sentence Transformers 官方文件）**
- 作者／機構：Sentence Transformers（UKP Lab／Hugging Face 維護）
- 日期：未標日期
- 網址：<https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html>
- 主張：兩階段管線的標準寫法：先用 bi-encoder 或詞彙搜尋撈一大批候選，再用 cross-encoder 逐一打分重排。
- 引文：「Hence, in a second stage, we use a re-ranker based on a CrossEncoder that scores the relevancy of all candidates for the given search query.」
- 核對：網頁全文比對
- 適合：R06（管線圖）

**R06-5　An Overview of Cohere's Rerank Model（Cohere 官方文件）**
- 作者／機構：Cohere
- 日期：未標日期
- 網址：<https://docs.cohere.com/docs/rerank-overview>
- 主張：託管式 rerank API 的用法：給 query 與文件清單，回傳依語意相關度排序的結果。Anthropic Contextual Retrieval 實驗用的就是 Cohere reranker。
- 引文：「Given a query and a list of documents , Rerank indexes the documents from most to least semantically relevant to the query.」（原文 documents 與逗號間有空格，照抄）
- 核對：網頁全文比對
- 適合：R06、R07

**R06-6　Rerankers（Voyage AI 官方文件）**
- 作者／機構：Voyage AI（MongoDB）
- 日期：頁面標示「Updated 23 days ago」（約 2026-09 底）
- 網址：<https://docs.voyageai.com/docs/reranker>
- 主張：說明 reranker 在管線中的位置：輸入通常是 embedding 檢索的初步結果，reranker 負責重新排序並給更準的相關分數。Claude 官方 embeddings 文件推薦的供應商。
- 引文：「The documents oftentimes are the preliminary results from an embedding-based retrieval system, and the reranker refines the ranks of these candidate documents and provides more accurate relevancy scores.」
- 核對：網頁全文比對
- 適合：R06

### R07　Anthropic 的 Contextual Retrieval

**R07-1　Introducing Contextual Retrieval（Anthropic）**
- 作者／機構：Anthropic（Engineering）
- 日期：2024-09-19
- 網址：<https://www.anthropic.com/research/contextual-retrieval>（原 `/news/contextual-retrieval` 轉址至此）
- 主張：傳統 RAG 切塊後會丟失上下文；做法是在嵌入與建 BM25 索引前，先用 Claude 替每個 chunk 加一段說明它在全文位置的脈絡。檢索失敗率降 49%，加上 reranking 降 67%。同一篇也說知識庫小於 20 萬 token 時直接整包放進 prompt 即可。
- 引文：「This method can reduce the number of failed retrievals by 49% and, when combined with reranking, by 67%.」
- 補充引文（R11 用）：「If your knowledge base is smaller than 200,000 tokens (about 500 pages of material), you can just include the entire knowledge base in the prompt that you give the model, with no need for RAG or similar methods.」
- 核對：網頁全文比對（兩句都比對過）
- 適合：R07（主文）、R05、R06、R11

**R07-2　Enhancing RAG with Contextual Retrieval（Anthropic cookbook）**
- 作者／機構：Anthropic
- 日期：未標日期（GitHub notebook 現行版）
- 網址：<https://github.com/anthropics/claude-cookbooks/blob/main/capabilities/contextual-embeddings/guide.ipynb>
- 主張：R07-1 的可執行版本，一步步示範基本 RAG、Contextual Embeddings、Contextual BM25、reranking，並用 prompt caching 壓低替每個 chunk 產生脈絡的成本。R07 的實作段可以照這份走。
- 引文：「Contextual Embeddings solve this problem by adding relevant context to each chunk before embedding.」
- 核對：notebook 原始檔全文比對（透過 raw.githubusercontent.com 抓取）
- 適合：R07（實作）

**R07-3　Prompt caching（Claude 官方文件）**
- 作者／機構：Anthropic
- 日期：未標日期
- 網址：<https://platform.claude.com/docs/en/build-with-claude/prompt-caching>
- 主張：Contextual Retrieval 的成本前提：替同一份文件的每個 chunk 產生脈絡時，整份文件是重複的前綴，可以快取，後續呼叫只付快取讀取的價格。
- 引文：「Prompt caching optimizes your API usage by allowing resuming from specific prefixes in your prompts.」
- 核對：網頁全文比對
- 適合：R07（成本）、R11

（對照組另見 R02-6 Late Chunking：同樣處理「chunk 失去脈絡」，但不呼叫 LLM，改在 embedding 模型內部做。）

### R08　GraphRAG

**R08-1　From Local to Global: A Graph RAG Approach to Query-Focused Summarization**
- 作者／機構：Darren Edge、Ha Trinh、Newman Cheng 等 10 人（Microsoft Research）
- 日期：2024-04-24（arXiv v1）
- 網址：<https://arxiv.org/abs/2404.16130>
- 主張：一般 RAG 答不了「這批資料的主題是什麼」這種針對整個語料的全域問題；GraphRAG 先用 LLM 抽出實體知識圖、預先產生社群摘要，再以 map-reduce 方式回答。在百萬 token 等級資料上，答案的完整度與多樣性明顯較好。
- 引文：「However, RAG fails on global questions directed at an entire text corpus, such as "What are the main themes in the dataset?", since this is inherently a query-focused summarization (QFS) task, rather than an explicit retrieval task.」
- 核對：arXiv 摘要逐字比對
- 適合：R08（主文）

**R08-2　GraphRAG 官方文件：Welcome／GraphRAG vs Baseline RAG**
- 作者／機構：Microsoft（GraphRAG 專案）
- 日期：未標日期
- 網址：<https://microsoft.github.io/graphrag/>
- 主張：官方把一般向量相似度檢索稱為「Baseline RAG」，指出它在「需要串起多筆資訊」與「整體性理解大量資料」兩種情況表現很差。
- 引文：「Baseline RAG performs poorly when being asked to holistically understand summarized semantic concepts over large data collections or even singular large documents.」
- 核對：網頁全文比對
- 適合：R08

**R08-3　GraphRAG 官方文件：Getting Started 與 Query Overview**
- 作者／機構：Microsoft（GraphRAG 專案）
- 日期：未標日期
- 網址：<https://microsoft.github.io/graphrag/get_started/>、<https://microsoft.github.io/graphrag/query/overview/>
- 主張：Query Overview 說明 Local、Global、DRIFT、Basic 四種查詢模式；Getting Started 明白提醒建索引很花錢，要先用小資料與便宜模型試。
- 引文：「We strongly recommend starting with the tutorial dataset here until you understand how the system works, and consider experimenting with fast/inexpensive models first before committing to a big indexing job.」
- 核對：網頁全文比對（Getting Started 頁）
- 適合：R08（成本警告，見第 3 節衝突 5）

**R08-4　GraphRAG: Unlocking LLM discovery on narrative private data（Microsoft Research 部落格）**
- 作者／機構：Jonathan Larson、Steven Truitt（Microsoft Research）
- 日期：2024-02-13（作者與日期由 GraphRAG 官方文件的 Blog Posts 頁核對）
- 網址：<https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/>
- 主張：GraphRAG 首次公開發表的部落格文，用 VIINA 新聞資料集示範。
- 引文：**未核對全文**。microsoft.com 研究部落格從本環境抓取回應 502／403，無法比對原文，此處不放引文。撰寫時若要引用，請在瀏覽器開原文自行抄錄。
- 適合：R08（歷史脈絡）

**R08-5　LazyGraphRAG: Setting a new standard for quality and cost（Microsoft Research 部落格）**
- 作者／機構：Darren Edge、Ha Trinh、Jonathan Larson（Microsoft Research）
- 日期：2024-11-25（作者與日期由 GraphRAG 官方文件的 Blog Posts 頁核對）
- 網址：<https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/>
- 主張（依搜尋引擎摘要，未讀原文）：不做預先摘要，索引成本與向量 RAG 相當、約為完整 GraphRAG 的 0.1%；這等於微軟自己承認完整 GraphRAG 的索引成本對部分使用者過高。
- 引文：**未核對全文**。原因同 R08-4。上述數字只來自搜尋摘要，寫進網頁前必須開原文確認。
- 適合：R08（成本，見第 3 節衝突 5）

**R08-6　RAG vs. GraphRAG: A Systematic Evaluation and Key Insights**
- 作者／機構：Haoyu Han、Li Ma、Yu Wang 等 12 人
- 日期：2025-02-17（arXiv v1；目前 v3）
- 網址：<https://arxiv.org/abs/2502.11371>
- 主張：在統一的前處理、檢索與生成設定下比較 RAG 與 GraphRAG，發現兩者在不同任務各有強項，合併使用效果最好；也指出既有 GraphRAG 評估協定不一致。
- 引文：「Our results highlight the distinct strengths of RAG and GraphRAG across different tasks and evaluation perspectives.」
- 核對：arXiv 摘要逐字比對
- 適合：R08（什麼時候不需要圖）

**R08-7　LightRAG: Simple and Fast Retrieval-Augmented Generation**
- 作者／機構：Zirui Guo、Lianghao Xia、Yanhua Yu 等 5 人（香港大學 HKUDS 等）
- 日期：2024-10-08（arXiv v1）
- 網址：<https://arxiv.org/abs/2410.05779>
- 主張：圖結構結合向量表示的雙層檢索，並支援增量更新，主打比 GraphRAG 更輕量。開源實作熱門，適合當「GraphRAG 的輕量替代」例子。
- 引文：「This capability is further enhanced by an incremental update algorithm that ensures the timely integration of new data, allowing the system to remain effective and responsive in rapidly changing data environments.」
- 核對：arXiv 摘要逐字比對
- 適合：R08

**R08-8　HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models**
- 作者／機構：Bernal Jiménez Gutiérrez、Yiheng Shu、Yu Gu 等 5 人（Ohio State University）
- 日期：2024-05-23（arXiv v1；NeurIPS 2024）
- 網址：<https://arxiv.org/abs/2405.14831>
- 主張：知識圖加 Personalized PageRank 做多跳問答，單步檢索就能接近或超過迭代式檢索（IRCoT），成本低 10–30 倍。
- 引文：「Single-step retrieval with HippoRAG achieves comparable or better performance than iterative retrieval like IRCoT while being 10-30 times cheaper and 6-13 times faster, and integrating HippoRAG into IRCoT brings further substantial gains.」
- 核對：arXiv 摘要逐字比對
- 適合：R08（多跳問題）

### R09　Agentic RAG 與工具呼叫

**R09-1　ReAct: Synergizing Reasoning and Acting in Language Models**
- 作者／機構：Shunyu Yao、Jeffrey Zhao、Dian Yu 等 7 人（Princeton、Google）
- 日期：2022-10-06（arXiv v1；ICLR 2023）
- 網址：<https://arxiv.org/abs/2210.03629>
- 主張：讓模型交錯產生推理與行動，行動可以呼叫知識庫等外部來源；在 HotpotQA 上靠呼叫 Wikipedia API 減少幻覺。這是「agent 自己決定去查」的原型。
- 引文：「Concretely, on question answering (HotpotQA) and fact verification (Fever), ReAct overcomes issues of hallucination and error propagation prevalent in chain-of-thought reasoning by interacting with a simple Wikipedia API, and generates human-like task-solving trajectories that are more interpretable than baselines without reasoning traces.」
- 核對：arXiv 摘要逐字比對
- 適合：R09（起源）

**R09-2　Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection**
- 作者／機構：Akari Asai、Zeqiu Wu、Yizhong Wang 等 5 人（University of Washington、AI2、IBM）
- 日期：2023-10-17（arXiv v1；ICLR 2024）
- 網址：<https://arxiv.org/abs/2310.11511>
- 主張：不管需不需要都塞固定數量的檢索段落，反而會傷害回答；Self-RAG 訓練模型自己判斷何時檢索、並批判檢索到的內容。
- 引文：「However, indiscriminately retrieving and incorporating a fixed number of retrieved passages, regardless of whether retrieval is necessary, or passages are relevant, diminishes LM versatility or can lead to unhelpful response generation.」
- 核對：arXiv 摘要逐字比對
- 適合：R09、R12

**R09-3　Active Retrieval Augmented Generation（FLARE）**
- 作者／機構：Zhengbao Jiang、Frank F. Xu、Luyu Gao 等 9 人（Carnegie Mellon University 等）
- 日期：2023-05-11（arXiv v1；EMNLP 2023）
- 網址：<https://arxiv.org/abs/2305.06983>
- 主張：一次檢索完就生成，不適合長文；FLARE 在生成過程中預測下一句，遇到低信心內容才再檢索。
- 引文：「Most existing retrieval augmented LMs employ a retrieve-and-generate setup that only retrieves information once based on the input.」
- 核對：arXiv 摘要逐字比對
- 適合：R09（多次檢索）

**R09-4　Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG**
- 作者／機構：Aditi Singh、Abul Ehtesham、Saket Kumar 等 5 人
- 日期：2025-01-15（arXiv v1；目前 v4）
- 網址：<https://arxiv.org/abs/2501.09136>
- 主張：傳統 RAG 流程固定，難以處理多步推理；Agentic RAG 把反思、規劃、工具使用、多代理協作放進管線，並提出依代理數量、控制結構等的分類。
- 引文：「Agentic Retrieval-Augmented Generation (Agentic RAG) transcends these limitations by embedding autonomous AI agents into the RAG pipeline.」
- 核對：arXiv 摘要逐字比對
- 適合：R09（分類地圖）

**R09-5　Retrieval：Agentic RAG 段（LangChain 官方文件）**
- 作者／機構：LangChain
- 日期：未標日期
- 網址：<https://docs.langchain.com/oss/python/deepagents/retrieval>（與 R01-5 同頁，引不同段落）
- 主張：框架文件對 Agentic RAG 的定義：不是先檢索再回答，而是 agent 在對話中逐步推理、自己決定何時以及如何檢索。
- 引文：「Instead of retrieving documents before answering, an agent (powered by an LLM) reasons step-by-step and decides when and how to retrieve information during the interaction.」
- 核對：網頁全文比對
- 適合：R09

**R09-6　Effective context engineering for AI agents（Anthropic）**
- 作者／機構：Anthropic（Engineering）
- 日期：2025-09-29
- 網址：<https://www.anthropic.com/research/effective-context-engineering-for-ai-agents>
- 主張：站內已引過這篇的 context rot 段（見第 1 節）。本系列要引的是「Context retrieval and agentic search」一節：從預先做 embedding 檢索，轉向 agent 只拿檔案路徑等輕量識別、需要時才去讀的「just in time」策略；Claude Code 就是用 glob、grep 即時取檔，避開索引過時的問題。
- 引文：「As the field transitions to more agentic approaches, we increasingly see teams augmenting these retrieval systems with “just in time” context strategies.」（原文用彎引號）
- 補充引文：「Claude Code is an agent that employs this hybrid model: CLAUDE.md files are naively dropped into context up front, while primitives like glob and grep allow it to navigate its environment and retrieve files just-in-time, effectively bypassing the issues of stale indexing and complex syntax trees.」
- 核對：網頁全文比對（兩句都比對過）
- 適合：R09（主文，可連到站內 harness、subagent 頁）、R11

**R09-7　Building effective agents（Anthropic）**
- 作者／機構：Erik Schluntz、Barry Zhang（Anthropic）
- 日期：2024-12-19
- 網址：<https://www.anthropic.com/research/building-effective-agents>
- 主張：agent 的基本單元是「加了檢索、工具、記憶的 LLM」；但很多應用用單次呼叫加檢索就夠，不必一開始就上 agent。適合在 R09 收尾提醒「不是每個 RAG 都要 agentic」。
- 引文：「For many applications, however, optimizing single LLM calls with retrieval and in-context examples is usually enough.」
- 核對：網頁全文比對
- 適合：R09（何時不要用 agentic RAG）

**R09-8　How we built our multi-agent research system（Anthropic）**
- 作者／機構：Anthropic（Engineering）
- 日期：2025-06-13
- 網址：<https://www.anthropic.com/research/multi-agent-research-system>
- 主張：Claude Research 功能的架構：主 agent 規劃研究流程，再派出平行的子 agent 同時搜尋。是「多代理平行檢索」的一手案例。站內 `docs/harness.md:29` 的來源表與 `:293` 的參考資料已列這篇（用途寫「平行化的代價」），本系列引的是架構描述。
- 引文：「Our Research feature involves an agent that plans a research process based on user queries, and then uses tools to create parallel agents that search for information simultaneously.」
- 核對：網頁全文比對
- 適合：R09

### R10　RAG 評估（RAGAS 等）

**R10-1　Ragas: Automated Evaluation of Retrieval Augmented Generation**
- 作者／機構：Shahul Es、Jithin James、Luis Espinosa-Anke、Steven Schockaert（Exploding Gradients、Cardiff University）
- 日期：2023-09-26（arXiv v1；EACL 2024 Demo）
- 網址：<https://arxiv.org/abs/2309.15217>
- 主張：提出不需人工標註參考答案的 RAG 評估指標組，分別評檢索是否找到相關且聚焦的段落、生成是否忠於段落、回答本身品質。
- 引文：「We introduce Ragas (Retrieval Augmented Generation Assessment), a framework for reference-free evaluation of Retrieval Augmented Generation (RAG) pipelines.」
- 核對：arXiv 摘要逐字比對
- 適合：R10（主文）

**R10-2　Ragas 文件：Faithfulness 與 Context Precision**
- 作者／機構：Ragas 專案（文件頁標示 `vibrantlabsai/ragas`）
- 日期：未標日期
- 網址：<https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/>、<https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_precision/>
- 主張：指標的現行定義。Faithfulness：回答中每一個主張都能被檢索內容支持才算忠實；Context Precision：相關 chunk 是否排在前面。
- 引文：「A response is considered faithful if all its claims can be supported by the retrieved context.」
- 補充引文：「Context Precision is a metric that evaluates the retriever's ability to rank relevant chunks higher than irrelevant ones for a given query in the retrieved context.」
- 核對：網頁全文比對（兩頁都比對過）
- 適合：R10（指標定義）

**R10-3　ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems**
- 作者／機構：Jon Saad-Falcon、Omar Khattab、Christopher Potts、Matei Zaharia（Stanford）
- 日期：2023-11-16（arXiv v1；NAACL 2024）
- 網址：<https://arxiv.org/abs/2311.09476>
- 主張：同樣評上下文相關性、回答忠實度、回答相關性三個面向，但用合成資料微調小型評審模型，並用幾百筆人工標註做 prediction-powered inference 校正誤差。
- 引文：「To mitigate potential prediction errors, ARES utilizes a small set of human-annotated datapoints for prediction-powered inference (PPI).」
- 核對：arXiv 摘要逐字比對
- 適合：R10（見第 3 節衝突 6）

**R10-4　The RAG Triad（TruLens 官方文件）**
- 作者／機構：TruLens（原 TruEra 開發，現由 Snowflake 維護）
- 日期：未標日期
- 網址：<https://www.trulens.org/getting_started/core_concepts/rag_triad/>
- 主張：把 RAG 評估拆成 context relevance、groundedness、answer relevance 三條邊。OWASP LLM01 的防護建議也引用了 RAG Triad。
- 引文：「The RAG triad is made up of 3 evaluations: context relevance, groundedness and answer relevance.」
- 核對：網頁全文比對
- 適合：R10、R12

**R10-5　Evaluation of Retrieval-Augmented Generation: A Survey**
- 作者／機構：Hao Yu、Aoran Gan、Kai Zhang 等 6 人
- 日期：2024-05-13（arXiv v1）
- 網址：<https://arxiv.org/abs/2405.07437>
- 主張：整理現有 RAG 基準的檢索與生成指標，並指出 RAG 因為混合結構、依賴動態知識源，評估特別難。
- 引文：「Evaluating these RAG systems, however, poses unique challenges due to their hybrid structure and reliance on dynamic knowledge sources.」
- 核對：arXiv 摘要逐字比對
- 適合：R10（指標總覽）

**R10-6　Benchmarking Large Language Models in Retrieval-Augmented Generation（RGB）**
- 作者／機構：Jiawei Chen、Hongyu Lin、Xianpei Han、Le Sun（中國科學院軟體研究所）
- 日期：2023-09-04（arXiv v1；AAAI 2024）
- 網址：<https://arxiv.org/abs/2309.01431>
- 主張：從雜訊韌性、拒答能力、資訊整合、反事實韌性四個能力評 LLM 在 RAG 下的表現，含中英文資料。結論是模型最弱的是「該拒答時拒答」與處理錯誤資訊。
- 引文：「Evaluation reveals that while LLMs exhibit a certain degree of noise robustness, they still struggle significantly in terms of negative rejection, information integration, and dealing with false information.」
- 核對：arXiv 摘要逐字比對
- 適合：R10、R12

### R11　長上下文模型和 RAG 的取捨

**R11-1　Lost in the Middle: How Language Models Use Long Contexts**
- 作者／機構：Nelson F. Liu、Kevin Lin、John Hewitt 等 7 人（Stanford 等）
- 日期：2023-07-06（arXiv v1；TACL 2024）
- 網址：<https://arxiv.org/abs/2307.03172>
- 主張：相關資訊放在輸入開頭或結尾時表現最好，放在中間時明顯變差，連長上下文模型也一樣。這直接影響 RAG 把檢索結果放在 prompt 哪裡。
- 引文：「In particular, we observe that performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts, even for explicitly long-context models.」
- 核對：arXiv 摘要逐字比對
- 適合：R11、R12

**R11-2　Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach（Self-Route）**
- 作者／機構：Zhuowan Li、Cheng Li、Mingyang Zhang 等 5 人（Google DeepMind、University of Michigan）
- 日期：2024-07-23（arXiv v1；EMNLP 2024 Industry）
- 網址：<https://arxiv.org/abs/2407.16833>
- 主張：資源足夠時，長上下文平均表現穩定勝過 RAG，但 RAG 便宜很多；提出讓模型自評後把問題分流到 RAG 或長上下文的 Self-Route。
- 引文：「Results reveal that when resourced sufficiently, LC consistently outperforms RAG in terms of average performance.」
- 核對：arXiv 摘要逐字比對
- 適合：R11（見第 3 節衝突 1）

**R11-3　In Defense of RAG in the Era of Long-Context Language Models（OP-RAG）**
- 作者／機構：Tan Yu、Anbang Xu、Rama Akkiraju（NVIDIA）
- 日期：2024-09-03（arXiv v1）
- 網址：<https://arxiv.org/abs/2409.01666>
- 主張：跟 R11-2 唱反調：超長上下文會稀釋對相關資訊的注意力；保留原文順序的 RAG（OP-RAG）用少很多的 token 就能比整包丟進長上下文更好，檢索塊數與品質呈倒 U 形。
- 引文：「There exist sweet points where OP-RAG could achieve higher answer quality with much less tokens than long-context LLM taking the whole context as input.」
- 核對：arXiv 摘要逐字比對
- 適合：R11（見第 3 節衝突 1）

**R11-4　Long-Context LLMs Meet RAG: Overcoming Challenges for Long Inputs in RAG**
- 作者／機構：Bowen Jin、Jinsung Yoon、Jiawei Han、Sercan O. Arik（Google Cloud AI Research、UIUC）
- 日期：2024-10-08（arXiv v1；ICLR 2025）
- 網址：<https://arxiv.org/abs/2410.05983>
- 主張：直覺以為長上下文模型可以塞更多檢索段落、recall 更高就更好，實際上段落數增加到某個程度品質會下降，主因是「難負例」（看起來相關其實不相關）的干擾。
- 引文：「However, our empirical findings demonstrate that for many long-context LLMs, the quality of generated output initially improves first, but then subsequently declines as the number of retrieved passages increases.」
- 核對：arXiv 摘要逐字比對
- 適合：R11、R12

**R11-5　RULER: What's the Real Context Size of Your Long-Context Language Models?**
- 作者／機構：Cheng-Ping Hsieh、Simeng Sun、Samuel Kriman 等 8 人（NVIDIA）
- 日期：2024-04-09（arXiv v1；COLM 2024）
- 網址：<https://arxiv.org/abs/2404.06654>
- 主張：大海撈針（NIAH）測試只量到表面能力；在多針、多跳、聚合任務下，宣稱支援 32K 以上的模型只有一半能在 32K 維持水準。
- 引文：「While these models all claim context sizes of 32K tokens or greater, only half of them can maintain satisfactory performance at the length of 32K.」
- 核對：arXiv 摘要逐字比對
- 適合：R11（宣稱長度 ≠ 有效長度）

**R11-6　Context Rot: How Increasing Input Tokens Impacts LLM Performance（Chroma 技術報告）**
- 作者／機構：Kelly Hong、Anton Troynikov、Jeff Huber（Chroma）
- 日期：2025-07-14
- 網址：<https://www.trychroma.com/research/context-rot>
- 主張：測了多個前沿模型，即使任務很簡單，輸入變長表現就變得不可靠，而且衰退是不均勻的。Anthropic 談 context rot 時引用的研究方向與此相同（站內 `docs/agent-basics.md:34` 已用 Anthropic 版本解釋，這裡補實驗來源）。
- 引文：「Our results reveal that models do not use their context uniformly; instead, their performance grows increasingly unreliable as input length grows.」
- 核對：網頁全文比對
- 適合：R11

**R11-7　Long context（Gemini API 官方文件）**
- 作者／機構：Google
- 日期：頁面標示 Last updated 2026-10-15
- 網址：<https://ai.google.dev/gemini-api/docs/long-context>
- 主張：長上下文廠商的立場：上下文短的模型才需要 RAG、摘要、丟棄舊訊息等策略，百萬 token 讓直接放進上下文變成可行選項；但同頁也承認單針測試之外表現差異很大，要撈多筆資訊時成本會疊加。
- 引文：「The more limited context windows common in many other models often require strategies like arbitrarily dropping old messages, summarizing content, using RAG with vector databases, or filtering prompts to save tokens.」
- 補充引文：「Performance can vary to a wide degree depending on the context.」
- 核對：網頁全文比對（兩句都比對過）
- 適合：R11（見第 3 節衝突 1）

**R11-8　Long context prompting（Claude 官方文件，Prompting best practices 內段落）**
- 作者／機構：Anthropic
- 日期：未標日期
- 網址：<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#long-context-prompting>（原 `long-context-tips` 頁轉址至此）
- 主張：20k token 以上的長文件，放在 prompt 最上面、問題放最後，並先請 Claude 摘錄相關引文再作答。這是 RAG 把檢索結果塞進 prompt 時的排版規則。
- 引文：「Put long-form data at the top: Place your long documents and inputs near the top of your prompt, above your query, instructions, and examples.」
- 核對：網頁全文比對
- 適合：R11、R07

（另見 R07-1 的 20 萬 token 門檻那句。）

### R12　常見失敗模式與經由檢索內容的 prompt injection

**R12-1　Seven Failure Points When Engineering a Retrieval Augmented Generation System**
- 作者／機構：Scott Barnett、Stefanus Kurniawan、Srikanth Thudumu 等 5 人（Deakin University）
- 日期：2024-01-11（arXiv v1；CAIN 2024）
- 網址：<https://arxiv.org/abs/2401.05856>
- 主張：從研究、教育、生醫三個實際專案整理出 RAG 的七個失敗點；兩個結論是 RAG 只能在上線運作中驗證，而且穩健性是逐步演進出來的、不是一開始就設計得出來。
- 引文：「The two key takeaways arising from our work are: 1) validation of a RAG system is only feasible during operation, and 2) the robustness of a RAG system evolves rather than designed in at the start.」
- 核對：arXiv 摘要逐字比對
- 適合：R12（失敗模式主文）、R10

**R12-2　Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection**
- 作者／機構：Kai Greshake、Sahar Abdelnabi、Shailesh Mishra 等 6 人（CISPA 等）
- 日期：2023-02-23（arXiv v1；AISec 2023）
- 網址：<https://arxiv.org/abs/2302.12173>
- 主張：「間接 prompt injection」的奠基論文。攻擊者不必直接跟模型對話，只要把指令藏進可能被檢索到的資料裡；LLM 應用模糊了資料與指令的界線。
- 引文：「We reveal new attack vectors, using Indirect Prompt Injection, that enable adversaries to remotely (without a direct interface) exploit LLM-integrated applications by strategically injecting prompts into data likely to be retrieved.」
- 核對：arXiv 摘要逐字比對
- 適合：R12（主文）

**R12-3　PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models**
- 作者／機構：Wei Zou、Runpeng Geng、Binghui Wang、Jinyuan Jia（Penn State 等）
- 日期：2024-02-12（arXiv v1；USENIX Security 2025）
- 網址：<https://arxiv.org/abs/2402.07867>
- 主張：知識庫本身就是攻擊面；在百萬筆文本的知識庫裡，每個目標問題只要注入 5 筆惡意文本，就能有 90% 成功率讓模型給出攻擊者指定的答案，既有防禦不足。
- 引文：「Our results show PoisonedRAG could achieve a 90% attack success rate when injecting five malicious texts for each target question into a knowledge database with millions of texts.」
- 核對：arXiv 摘要逐字比對
- 適合：R12（知識庫投毒）

**R12-4　LLM01:2025 Prompt Injection（OWASP Top 10 for LLM Applications）**
- 作者／機構：OWASP GenAI Security Project
- 日期：2025 版
- 網址：<https://genai.owasp.org/llmrisk/llm01-prompt-injection/>
- 主張：業界最常引用的風險清單第一名；明講 RAG 與微調都不能完全消除 prompt injection，間接注入來自網站或檔案等外部來源。
- 引文：「While techniques like Retrieval Augmented Generation (RAG) and fine-tuning aim to make LLM outputs more relevant and accurate, research shows that they do not fully mitigate prompt injection vulnerabilities.」
- 核對：網頁全文比對
- 適合：R12

**R12-5　LLM08:2025 Vector and Embedding Weaknesses（OWASP Top 10 for LLM Applications）**
- 作者／機構：OWASP GenAI Security Project
- 日期：2025 版
- 網址：<https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/>
- 主張：2025 版新增的 RAG 專屬風險：向量與 embedding 在產生、儲存、檢索各環節都可能被利用，包括存取控制不當造成資料外洩、資料投毒等。
- 引文：「Weaknesses in how vectors and embeddings are generated, stored, or retrieved can be exploited by malicious actions (intentional or unintentional) to inject harmful content, manipulate model outputs, or access sensitive information.」
- 核對：網頁全文比對
- 適合：R12、R04（權限與多租戶）

**R12-6　NIST AI 100-2 E2025：Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations**
- 作者／機構：Apostol Vassilev、Alina Oprea、Alie Fordyce 等（NIST 等）
- 日期：2025-03
- 網址：<https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf>（DOI 10.6028/NIST.AI.100-2e2025）
- 主張：美國標準機構的對抗式機器學習分類，把間接 prompt injection 列為生成式 AI 的主要攻擊類型，根源是資料與指令共用同一個通道。
- 引文：「Because GenAI models combine the data and instruction channels, attackers can leverage the data channel to affect system operations by manipulating resources with which the system interacts.」
- 核對：PDF 全文比對
- 適合：R12（術語與分類）

**R12-7　How Microsoft defends against indirect prompt injection attacks（MSRC 部落格）**
- 作者／機構：Andrew Paverd（Microsoft Security Response Center）
- 日期：2025-07-29
- 網址：<https://www.microsoft.com/en-us/msrc/blog/2025/07/how-microsoft-defends-against-indirect-prompt-injection-attacks>
- 主張：大廠的縱深防禦做法：強化 system prompt、用 Spotlighting 隔離不信任輸入、偵測，加上資料治理與確定性地封鎖已知外洩手法；並說間接注入是 LLM 機率式生成的固有風險。
- 引文：「Indirect prompt injection is an inherent risk that arises from the probabilistic language modelling, stochastic generation, and linguistic flexibility of modern LLMs 2 .」（句尾「2」是原文註腳編號，照抄）
- 核對：網頁全文比對
- 適合：R12（防禦）

**R12-8　Mitigate jailbreaks and prompt injections（Claude 官方文件）**
- 作者／機構：Anthropic
- 日期：未標日期
- 網址：<https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks>
- 主張：把威脅分成「使用者本身是攻擊者」與「使用者可信、但 Claude 讀到的第三方內容有惡意指令」兩類；後者建議把不信任內容只放在 tool result 裡，讓 Claude 能分辨。這對 RAG 的意義是：檢索結果放哪裡會影響防禦。
- 引文：「Indirect prompt injection , where the user is trusted but Claude processes third-party content (webpages, emails, documents, tool results) that contains adversarial instructions.」（原文 injection 與逗號間有空格，照抄）
- 補充引文：「Structure your application so that Claude can reliably distinguish untrusted content from your instructions: Put untrusted content only in tool results.」
- 核對：網頁全文比對（兩句都比對過）
- 適合：R12（Claude 的具體建議）

**R12-9　Mitigating the risk of prompt injections in browser use（Anthropic）**
- 作者／機構：Anthropic（Alignment）
- 日期：2025-11-24
- 網址：<https://www.anthropic.com/research/prompt-injection-defenses>
- 主張：Anthropic 自己承認模型的 prompt injection 韌性雖有進步，但問題遠未解決，尤其模型能採取越多實際行動時。適合在 R12 結尾校準讀者期待。
- 引文：「But prompt injection is far from a solved problem, particularly as models take more real-world actions.」
- 核對：網頁全文比對
- 適合：R12

**R12-10　Security：Protect against prompt injection（Claude Code 官方文件）**
- 作者／機構：Anthropic
- 日期：未標日期
- 網址：<https://code.claude.com/docs/en/security>
- 主張：站內 `docs/mcp.md:140-142` 已引同一頁的 MCP 段與五點建議。本系列只需要這頁對 prompt injection 的定義，其餘直接連回 mcp.md。
- 引文：「Prompt injection is a technique where an attacker attempts to override or manipulate an AI assistant’s instructions by inserting malicious text.」（原文用彎撇號）
- 核對：網頁全文比對
- 適合：R12（定義；其餘連回站內）

---

## 3. 來源之間說法衝突的主題

寫網頁時，這些地方不能只引一邊。

1. **長上下文會不會取代 RAG（R11）**
   - 長上下文較好：R11-2 Self-Route（資源足夠時長上下文平均穩定勝出）、R11-7 Gemini 文件（百萬 token 讓 RAG 不再是必要手段）、R07-1 Anthropic（20 萬 token 以下直接整包放進 prompt）。
   - RAG 較好或長上下文有隱憂：R11-3 OP-RAG（RAG 用更少 token 拿到更好品質）、R11-1 Lost in the Middle、R11-5 RULER、R11-6 Context Rot（輸入越長越不可靠）、R11-4（塞越多段落反而變差）。
   - 調和方向：比較基準不同（模型世代、任務、是否計成本）。R11-2 自己也提出分流，R11-7 同頁也承認多筆資訊檢索的成本與表現差異。網頁應寫成「依知識庫大小、更新頻率、成本與問題類型選擇」，不宜下單一結論。

2. **語意切塊值不值得（R02）**
   - 正方：R02-5 LlamaIndex 提供語意切塊器作為一級功能。
   - 反方：R02-2 指出計算成本換不到穩定效果；R02-4 LangChain 建議多數情況從遞迴字元切塊開始。
   - 第三方：R02-1 Chroma 說切法影響可達 9% recall，但也發現熱門切塊器的預設值本身就可能很差，所以「哪種切法好」高度依賴資料與參數。

3. **稠密檢索 vs. BM25（R03、R05）**
   - R03-5 DPR：稠密檢索 top-20 準確率比 BM25 高 9–19 個百分點（在有訓練資料的開放領域問答）。
   - R05-3 BEIR：換到沒見過的領域，BM25 是穩健基準，稠密模型常常輸。
   - R07-1 Anthropic 與 R05-6 Pinecone 的實務結論是兩者並用。差異來自評測是否在訓練分布內，寫的時候要講清楚。

4. **Hybrid search 該用名次融合還是分數融合（R05）**
   - R05-2 RRF 原始論文與 R05-4 Elasticsearch：只看名次，不需調參。
   - R05-5 Weaviate：預設改用 `relativeScoreFusion`，理由是保留原始分數資訊比只保留名次多。
   - 兩者都是官方說法，各有預設，網頁應並列並說明取捨。

5. **GraphRAG 的效益與成本（R08）**
   - R08-1 原始論文：全域問題上答案完整度與多樣性大幅提升。
   - R08-6：統一設定比較後，RAG 與 GraphRAG 各有擅長任務，不是 GraphRAG 全面勝出。
   - R08-3 官方文件提醒建索引成本高；R08-5 LazyGraphRAG（**未核對全文**）宣稱把索引成本降到完整 GraphRAG 的約 0.1%，等於承認原版成本是門檻。R08-5 的數字寫進網頁前必須自行開原文確認。

6. **RAG 評估能不能完全交給 LLM 評審（R10）**
   - R10-1 Ragas：主打不需人工標註參考答案（reference-free）。
   - R10-3 ARES：仍需幾百筆人工標註來校正評審誤差。
   - R12-1：RAG 只能在上線運作中驗證。
   - R10-4 TruLens 文件說三項評估都過就能「confidence that our LLM app is free from hallucination」，這是全庫最強的說法，跟 R10-6 RGB 與 R12 系列的發現有張力，引用時要註明是工具文件的說法。

7. **RAG 能不能「解決幻覺」（R01、R12）**
   - R01-3 綜述與 R10-4 TruLens 把 RAG 定位為降低幻覺、提升可信度的方案。
   - R12-4 OWASP 明說 RAG 不能完全消除 prompt injection；R12-2、R12-3 指出檢索內容本身就是新的攻擊面；R10-6 RGB 顯示模型在拒答與錯誤資訊上仍明顯吃力。
   - 站內 `docs/projects.md:88` 與 `docs/mcp.md:133-134` 已經有「查得到不等於答得對」的立場，系列可以延續這條線。

8. **預先建向量索引 vs. agent 即時搜尋（R09）**
   - R09-6 Anthropic：Claude Code 不建向量索引，用 glob／grep 即時取檔，避開索引過時；但同文也說多數 AI 應用仍用 embedding 預先檢索，最有效的可能是混合策略。
   - R09-7 Anthropic：多數應用單次呼叫加檢索就夠。
   - R09-4 綜述與 R09-5 LangChain：把 agentic RAG 描述成傳統 RAG 的進化。
   - 不算正面衝突，但「agentic 一定比較好」的說法沒有共識，寫的時候要避免。

9. **Embedding 模型越大越好？（R03）**
   - R03-2 MMTEB：公開模型第一名只有 5.6 億參數。R03-1 MTEB：沒有任何方法在所有任務都最好。這不是兩個來源互相矛盾，而是跟「選最大的模型就對了」的常見印象衝突，值得在 R03 寫一段。

---

## 4. 系列分篇建議

| 篇號 | 標題（暫定） | 範圍（一句） | 主要來源 |
|---|---|---|---|
| R01 | RAG 是什麼：從 2020 年的論文到今天的產品 | RAG 的定義、為什麼需要外部記憶、2-step／agentic／hybrid 三型，以 Claude Projects 的 RAG 模式當生活例子（連到 `projects.md`）。 | R01-1、R01-2、R01-3、R01-4、R01-5 |
| R02 | 切塊：文件要切多大、怎麼切 | 固定長度、遞迴、語意、命題切塊的差別與實證，結論是要用自己的資料測。 | R02-1、R02-2、R02-3、R02-4、R02-5、R02-6 |
| R03 | Embedding：把文字變向量，以及怎麼讀 MTEB | bi-encoder 原理、向量距離的意義、MTEB／MMTEB 排行榜的讀法，與 Claude 沒有自家 embedding 這件事。 | R03-1、R03-2、R03-3、R03-4、R03-6、R03-7 |
| R04 | 向量資料庫與近似最近鄰 | 精確 vs. 近似搜尋、HNSW、量化、怎麼比較向量庫，以及用 pgvector 起步。 | R04-1、R04-2、R04-3、R04-4、R04-5、R12-5 |
| R05 | Hybrid search：BM25 沒有過時 | BM25 原理、稠密與詞彙檢索各自的盲點、RRF 與分數融合。 | R05-1、R05-2、R05-3、R05-4、R05-5、R05-6、R03-5 |
| R06 | Reranking：第二階段的精排 | bi-encoder、cross-encoder、late interaction、LLM 當 reranker 的成本與效果。 | R06-1、R06-2、R06-3、R06-4、R06-5、R06-6 |
| R07 | Contextual Retrieval 實作（用 Claude） | 照 Anthropic cookbook 走一遍，加上 prompt caching 成本計算與 late chunking 對照。 | R07-1、R07-2、R07-3、R02-6、R11-8 |
| R08 | GraphRAG：什麼問題才需要圖 | 全域問題 vs. 局部問題、GraphRAG 的查詢模式與索引成本、輕量替代方案。 | R08-1、R08-2、R08-3、R08-6、R08-7、R08-8（R08-4、R08-5 待核對全文） |
| R09 | Agentic RAG：讓 agent 決定什麼時候查 | ReAct 到 Self-RAG 的演進、Claude Code 的即時搜尋、多代理平行檢索，以及什麼時候不需要 agentic（連到 `harness.md`、`subagent.md`）。 | R09-1、R09-2、R09-3、R09-4、R09-5、R09-6、R09-7、R09-8 |
| R10 | 怎麼評估一個 RAG 系統 | 檢索指標與生成指標分開看、LLM 評審的可靠度、為什麼要留人工標註。 | R10-1、R10-2、R10-3、R10-4、R10-5、R10-6 |
| R11 | 長上下文時代還需要 RAG 嗎 | 兩派實證並列，給出依知識庫大小、成本、更新頻率的選擇判準。 | R11-1～R11-8、R07-1 |
| R12 | RAG 會怎麼壞：失敗模式與檢索內容裡的 prompt injection | 七個失敗點、知識庫投毒、間接注入的威脅模型與防禦（連到 `mcp.md` 第 7 節）。 | R12-1～R12-10、R10-6 |

建議閱讀順序：R01 → R02 → R03 → R04 → R05 → R06 → R07（前七篇是一條完整管線）→ R10（先學會量）→ R11 → R08 → R09 → R12。

---

## 5. 統計

| 主題 | 來源數 | 未核對全文 |
|---|---|---|
| R01 RAG 基本流程與原始論文 | 5 | 0 |
| R02 Chunking 策略 | 6 | 0 |
| R03 Embedding 模型與 MTEB | 7 | 0 |
| R04 向量資料庫與 ANN | 5 | 0 |
| R05 Hybrid search 與 BM25 | 6 | 0 |
| R06 Reranking | 6 | 0 |
| R07 Contextual Retrieval | 3 | 0 |
| R08 GraphRAG | 8 | 2（R08-4、R08-5） |
| R09 Agentic RAG 與工具呼叫 | 8 | 0 |
| R10 RAG 評估 | 6 | 0 |
| R11 長上下文與 RAG 的取捨 | 8 | 0 |
| R12 失敗模式與 prompt injection | 10 | 0 |
| **合計** | **78** | **2** |

- arXiv 論文的引文只跟摘要比對，論文內文的數字與實驗設定沒有逐一核對；寫網頁時若要引用摘要以外的內容，要再開 PDF。
- 「未標日期」的官方文件頁內容會變動，寫網頁時建議再開一次確認引文還在。
