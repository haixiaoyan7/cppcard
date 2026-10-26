#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C++ 面试口袋卡片 · 方案 B「追问链叙事」总结页生成器

与 _gen_summary.py（方案 A：按知识主题分 10 个 topic）并存。
本版把 86 题重新编排成「四篇 · 十五幕」的面试追问链，
把原本被知识分类拆开、其实是同一条线的题目重新缝合。

用法:
    python3 _gen_summary_b.py

产出:
    b-act-01-birth.html ... b-act-15-perf.html     （封面页 + 若干串讲页）
    index-b.html                                    （方案 B 总目录）

维护方式:
    - 编排以 summary-plan-b.md 为准；本文件 ACTS 与之对齐。
    - 卡片的「题目 / 一句话回答 / 是否高频」复用 _gen_summary.py，改动 ACTS 里的卡号顺序即可。
"""

import json
import os

# 复用方案 A 的卡片数据与页面模板（不改动 A 版任何内容）
from _gen_summary import TOPICS as A_TOPICS, TEMPLATE as A_TEMPLATE

HERE = os.path.dirname(os.path.abspath(__file__))
B_PER_PAGE = 4
B_FIRST_PAGE = 3  # 第二页（第一张串讲，含主线导语）最多 3 条


def b_page_count(n, first=None):
    """封面 + 串讲页。第一张串讲最多 first 条，其后按 B_PER_PAGE。"""
    cap = B_FIRST_PAGE if first is None else first
    if n <= cap:
        recap = 1
    else:
        recap = 1 + (n - cap + B_PER_PAGE - 1) // B_PER_PAGE
    return 1 + recap

# ---------------------------------------------------------------------------
# 1. 从方案 A 抽出「卡号 -> [卡号, 题目, 一句话回答, 是否高频]」查找表
# ---------------------------------------------------------------------------
CARD = {}
for _t in A_TOPICS:
    for _it in _t["items"]:
        CARD[_it[0]] = _it

# ---------------------------------------------------------------------------
# 2. 方案 B 的编排：四篇 · 十五幕
#    每一幕 cards 里只写卡号，题目/答案自动从 CARD 取，原卡号作为标注保留
# ---------------------------------------------------------------------------
ACTS = [
    # ===================== 篇一 · 一个对象的一生（幕 1–8，54 题）=====================
    {
        "slug": "b-act-01-birth", "no": "01",
        "part": "篇一 · 一个对象的一生", "part_en": "PART I · LIFE OF AN OBJECT",
        "cn": "诞生：住哪 · 谁拥有", "en": "BIRTH · MEMORY & OWNERSHIP",
        "line": "对象的第一课：它住在哪、怎么造出来、由谁归还。",
        "thread": "本幕从 <b>住哪</b> 问起：栈还是堆 → 怎么造出来（new / malloc）→ 内存怎么排（对齐）→ "
                  "分配与构造分离（placement new）→ 怎么指向它（指针 / 引用）→ "
                  "<b>谁负责释放（死亡契约）</b> → RAII 与智能指针把所有权模板化。"
                  "例：<b>LogMessage</b> 在内存池里 placement new，用 unique_ptr 持有。",
        "quote": "任何内存题，先抛「所有权 + 生命周期」这条主线，再落到具体语法。",
        "cards": ["004", "005", "007", "008", "001", "003", "002"],
    },
    {
        "slug": "b-act-02-polymorphism", "no": "02",
        "part": "篇一 · 一个对象的一生", "part_en": "PART I · LIFE OF AN OBJECT",
        "cn": "身份：多态与类型转换", "en": "POLYMORPHISM & CASTS",
        "line": "同一个指针，怎么调到对的函数，又怎么在类型之间转换？",
        "thread": "本幕主线是 <b>身份与绑定时机</b>：虚函数（vtable）→ 对象内存布局（058 与 vptr 并排）→ "
                  "构造/析构能否虚（多态对象的正确死亡）→ 纯虚 / 抽象 → 菱形 / 虚继承 → 继承语义 → "
                  "重载 / 重写 / 隐藏 → 类作用域里的 static（局部 static 是终章 063 的伏笔）→ "
                  "RTTI → 四种 cast → explicit 拦住隐式转换。封闭集合的多态见幕 6 的 variant。",
        "quote": "被追问细节时，用「这是编译期决议还是运行期决议」切入，胜过背十条结论。",
        "cards": ["009", "058", "012", "010", "011", "016", "017", "018", "014", "015", "019"],
    },
    {
        "slug": "b-act-03-value", "no": "03",
        "part": "篇一 · 一个对象的一生", "part_en": "PART I · LIFE OF AN OBJECT",
        "cn": "复制与转移", "en": "COPY & MOVE · VALUE SEMANTICS",
        "line": "有了对象，面试官立刻追问：复制它会发生什么？",
        "thread": "本幕追问链是 <b>值语义</b>：深浅拷贝与 Rule of 3/5 → 左值右值与移动语义 → "
                  "move / forward（forward 的引用折叠回看幕 5 的 032 / 026 / 035，emplace 就是完美转发）→ "
                  "RVO / NRVO → 源对象被掏空后仍要析构。扩容走移动还是拷贝，看移动构造是否 noexcept，回指幕 8 的 023。",
        "quote": "把「拷贝 → 移动 → 消除 → 空壳仍析构」讲成一条链；noexcept 留给幕 8，但这里要先埋下。",
        "cards": ["013", "020", "021", "022"],
        "first_page": 4,  # 第 2 页放满 4 条
    },
    {
        "slug": "b-act-04-container", "no": "04",
        "part": "篇一 · 一个对象的一生", "part_en": "PART I · LIFE OF AN OBJECT",
        "cn": "进容器：STL 与布局", "en": "CONTAINERS · STL & LAYOUT",
        "line": "对象被放进容器：存哪、怎么搬、旧元素怎么死。",
        "thread": "本幕主线：<b>对象进容器</b> → vector / deque / string 布局 → "
                  "扩容搬迁（承接幕 3；move_if_noexcept 回指幕 8 的 023）→ 旧元素怎么死 → "
                  "map vs unordered_map → 迭代器分类 → introsort → allocator。",
        "quote": "问「选哪个容器」时先反问访问模式：查找方式、是否有序、插入位置、元素大小。",
        "cards": ["038", "040", "044", "039", "041", "042", "043"],
    },
    {
        "slug": "b-act-05-compiletime", "no": "05",
        "part": "篇一 · 一个对象的一生", "part_en": "PART I · LIFE OF AN OBJECT",
        "cn": "被泛化：模板与编译期", "en": "TEMPLATES · COMPILE-TIME",
        "line": "对象被抽象成任意类型：模板是编译期的语言。",
        "thread": "本幕沿 <b>编译期控制流</b>：实例化 → 类型推导（auto / decltype，与模板推导同一套）→ "
                  "特化 → SFINAE → Concepts 换掉 SFINAE → 变参模板（回看 021：可变参数 + forward = emplace）→ "
                  "元编程 → constexpr 取代一部分元编程 → CRTP 编译期多态（对照幕 2 的虚函数）→ 结构化绑定。",
        "quote": "用「编译期的变量（类型）、分支（特化）、循环（变参）」类比开场，比逐条背语法专业。",
        "cards": ["032", "026", "033", "034", "030", "035", "036", "027", "037", "028"],
    },
    {
        "slug": "b-act-06-modern", "no": "06",
        "part": "篇一 · 一个对象的一生", "part_en": "PART I · LIFE OF AN OBJECT",
        "cn": "被函数式操作", "en": "CALLABLES · TYPE SAFETY",
        "line": "用 lambda / function 操作对象，用 optional / variant 取代魔法值。",
        "thread": "本幕收束 <b>可调用体与类型安全</b>：lambda 匿名闭包 → std::function 统一可调用体 → "
                  "optional / variant / any 用类型取代魔法值。"
                  "variant + visit 是封闭集合的多态，对照幕 2 的虚函数（开放集合、要虚析构）。",
        "quote": "现代特性题套路：先说解决什么痛点，再说代价，最后给一个项目里的落地场景。",
        "cards": ["024", "025", "029"],
    },
    {
        "slug": "b-act-07-concurrency", "no": "07",
        "part": "篇一 · 一个对象的一生", "part_en": "PART I · LIFE OF AN OBJECT",
        "cn": "被并发访问", "en": "CONCURRENCY · SHARED DATA & ASYNC",
        "line": "多线程同时碰它：加锁、无锁，还是挂起等待？",
        "thread": "本幕沿 <b>共享数据与异步</b>：起线程（join 之前对象必须还活着）→ 加锁与条件变量 → "
                  "锁选型 → 死锁 → 原子 / 无锁 / CAS → 线程池 → async / future → "
                  "协程挂起式异步（和线程不是一回事）。跨线程 shared_ptr 在哪个线程析构，留到幕 8 追问 002。",
        "quote": "并发题按「为什么会错 → 怎么修 → 代价是什么」三段讲，条理最清。",
        "cards": ["045", "046", "047", "052", "053", "049", "050", "051", "048", "031"],
    },
    {
        "slug": "b-act-08-death", "no": "08",
        "part": "篇一 · 一个对象的一生", "part_en": "PART I · LIFE OF AN OBJECT",
        "cn": "死亡：异常、泄漏与谢幕", "en": "DEATH · EXCEPTIONS & LEAKS",
        "line": "正常死亡已散落前幕；此处收异常中途的死亡与泄漏。",
        "thread": "本幕是 <b>对象生命的终幕</b>：正常死亡回指幕 1 的 RAII / 智能指针、幕 2 虚析构、"
                  "幕 3 移动后析构、幕 4 容器销毁 → 死途中抛异常（强保证：要么活、要么死干净；"
                  "noexcept 也决定幕 4 扩容走移动还是拷贝）→ 该死没死（泄漏）。"
                  "并发下谁先析构不单列卡片，追问 002 与 045。",
        "quote": "异常安全三保证必须能举例：vector 扩容为何要求移动构造 noexcept。",
        "cards": ["023", "006"],
    },
    # ===================== 篇二 · 一行代码到一条指令（幕 9，8 题）=====================
    {
        "slug": "b-act-09-lowlevel", "no": "09",
        "part": "篇二 · 一行代码到一条指令", "part_en": "PART II · CODE TO INSTRUCTION",
        "cn": "编译链接与底层机制", "en": "COMPILE · LINK · RUNTIME",
        "line": "跳出单个对象：一行代码怎样变成一条指令，又跑得多快？",
        "thread": "本幕讲 <b>代码到指令</b>：预处理 → 编译 → 汇编 → 链接 → ODR（回收幕 2 的 static 内部链接）/ ABI → "
                  "虚拟内存与分页 → 用户态 / 内核态 → cache 友好（false sharing 回收幕 1 的对齐，也是并发与 cache 的交汇）。",
        "quote": "「undefined / duplicate symbol 怎么排查」最实战，答 nm、objdump 比背概念加分。",
        "cards": ["054", "055", "056", "057", "059", "060", "061", "062"],
        "first_page": 4,  # 第二张、第三张各 4 条
    },
    # ===================== 篇三 · 一次请求的旅程（幕 10–12，18 题）=====================
    {
        "slug": "b-act-10-os-exec", "no": "10",
        "part": "篇三 · 一次请求的旅程", "part_en": "PART III · JOURNEY OF A REQUEST",
        "cn": "执行单元：进程 · fork · IPC", "en": "OS · PROCESS · IPC",
        "line": "可执行文件跑起来：谁在处理、怎么多进程、进程间怎么说话。",
        "thread": "本幕是 <b>OS 执行模型</b>：进程 / 线程 / 协程（概念层，C++20 实现见篇一 031）→ "
                  "fork 写时拷贝多一个进程 → IPC 选型（管道 / 共享内存 / socket 等）。",
        "quote": "先分清 OS 实体：进程隔离、线程共享、协程用户态调度——别和篇一 031 的 co_await 混为一谈。",
        "cards": ["075", "076", "077"],
    },
    {
        "slug": "b-act-11-net-io", "no": "11",
        "part": "篇三 · 一次请求的旅程", "part_en": "PART III · JOURNEY OF A REQUEST",
        "cn": "网络 IO 栈", "en": "NETWORK · MULTIPLEX · OPTIMIZE",
        "line": "对外服务：建连接、等事件、分发、少搬数据。",
        "thread": "本幕沿 <b>高并发网络 IO</b>：TCP 握手挥手 → select / poll / epoll → ET / LT → "
                  "Reactor 分发（handler 可配合篇一 031 协程）→ 零拷贝 / mmap → io_uring / 惊群。",
        "quote": "把 epoll、Reactor、零拷贝串成「一个连接从 accept 到响应」，一次讲透三题。",
        "cards": ["072", "070", "069", "071", "073", "074"],
    },
    {
        "slug": "b-act-12-database", "no": "12",
        "part": "篇三 · 一次请求的旅程", "part_en": "PART III · JOURNEY OF A REQUEST",
        "cn": "持久化与规模：数据库与分布式", "en": "DATABASE & DISTRIBUTED",
        "line": "请求落到存储层：正确性与速度如何两全？",
        "thread": "本幕主线是 <b>正确性 → 速度 → 缓存 → 多机</b>：ACID / 隔离级别 → MVCC → 三大日志 → "
                  "B+ 树索引与优化 → Redis 为什么快 → 结构与一致性 → 穿透 / 击穿 / 雪崩 → Raft。",
        "quote": "后端岗先问「读写比例和数据量」再展开，比直接背隔离级别定义专业。",
        "cards": ["078", "082", "081", "079", "080", "086", "084", "085", "083"],
    },
    # ===================== 终章 · 架构的落地（幕 13–15，6 题）=====================
    {
        "slug": "b-act-13-create", "no": "13",
        "part": "终章 · 架构的落地", "part_en": "FINALE · ARCHITECTURE IN PRACTICE",
        "cn": "创建与生命周期", "en": "CREATION & LIFETIME",
        "line": "组件的第一问：谁负责造它？全局要几个？",
        "thread": "本幕沿 <b>创建与生命周期</b>：工厂把构造与使用解耦 → "
                  "单例控制全局唯一实例（Meyer's + 线程安全）；"
                  "回指篇一 OOP / 智能指针、幕 7 并发、幕 2 的 018（局部 static）。",
        "quote": "先答「谁创建、谁持有、全局几个」，再展开实现细节。",
        "cards": ["064", "063"],
    },
    {
        "slug": "b-act-14-decouple", "no": "14",
        "part": "终章 · 架构的落地", "part_en": "FINALE · ARCHITECTURE IN PRACTICE",
        "cn": "解耦与封装", "en": "DECOUPLING & ENCAPSULATION",
        "line": "组件的第二问：怎么通知外界？怎么藏实现？",
        "thread": "本幕沿 <b>解耦与封装</b>：观察者/发布-订阅解耦通知链 → "
                  "PIMPL 隐藏实现、稳定 ABI、切断编译依赖；"
                  "回指篇一 lambda/function，篇二 ODR/ABI。",
        "quote": "用一层间接换可变性——但要说明代价：悬垂订阅者、堆分配、一次间接。",
        "cards": ["065", "066"],
    },
    {
        "slug": "b-act-15-perf", "no": "15",
        "part": "终章 · 架构的落地", "part_en": "FINALE · ARCHITECTURE IN PRACTICE",
        "cn": "性能工程", "en": "PERFORMANCE ENGINEERING",
        "line": "组件的第三问：热路径怎么分配？高并发怎么观测？",
        "thread": "本幕是 <b>用指标证明取舍</b>：内存池用定长块 + 空闲链表支撑热路径 O(1) 分配 → "
                  "日志系统用异步队列 + 批量落盘保吞吐；"
                  "回指幕 1 的 placement new / 对齐、幕 3 的移动、幕 8 的 noexcept、幕 7 无锁队列、篇三 IO。"
                  "内存池里 placement new 出 LogMessage，一条对象的一生在这里闭合。",
        "quote": "系统设计题必须给指标：吞吐、P99 延迟、内存占用，并说明你在哪个维度做了取舍。",
        "cards": ["068", "067"],
    },
]

PART_SHORT = {
    "篇一 · 一个对象的一生": "语言核心",
    "篇二 · 一行代码到一条指令": "编译与底层",
    "篇三 · 一次请求的旅程": "系统",
    "终章 · 架构的落地": "综合设计",
}

# 配色：篇一靛蓝；后三篇用电紫 / 电青 / 电绿，同色更深做第二色。橙色只留给 HOT。
ARC_GRADIENT = (
    "linear-gradient(90deg, "
    "#3b5bdb 0%, #6d28d9 34%, #0891b2 67%, #059669 100%)"
)

PART_THEME = {
    "篇一 · 一个对象的一生": {
        "accent": "#3b5bdb", "accent2": "#2746b0", "soft": "#eef1fb",
        "deep": "#1e3266", "rgb": "59,91,219", "rgb2": "39,70,176",
        "label": "OBJECT LIFE",
    },
    "篇二 · 一行代码到一条指令": {
        "accent": "#6d28d9", "accent2": "#4c1d95", "soft": "#f4f0ff",
        "deep": "#3b1570", "rgb": "109,40,217", "rgb2": "76,29,149",
        "label": "CODE TO INSTRUCTION",
    },
    "篇三 · 一次请求的旅程": {
        "accent": "#0891b2", "accent2": "#0e7490", "soft": "#e6f7fb",
        "deep": "#0f4c5c", "rgb": "8,145,178", "rgb2": "14,116,144",
        "label": "REQUEST JOURNEY",
    },
    "终章 · 架构的落地": {
        "accent": "#059669", "accent2": "#047857", "soft": "#ecfdf5",
        "deep": "#064e3b", "rgb": "5,150,105", "rgb2": "4,120,87",
        "label": "ARCHITECTURE",
    },
}

TOTAL_ACTS = len(ACTS)

# ---------------------------------------------------------------------------
# 3. 复用方案 A 的页面模板，仅把措辞从「模块 / TOPIC」改为「幕 / STORYLINE」
# ---------------------------------------------------------------------------
B_THEME_CSS = r"""
  /* ===== 方案 B：墨色四章（默认篇一，各幕由 JS 注入篇章色） ===== */
  :root {
    --theme: #3b5bdb;
    --theme-2: #2746b0;
    --theme-soft: #eef1fb;
    --theme-deep: #1e3266;
    --theme-rgb: 59,91,219;
    --theme2-rgb: 39,70,176;
    --paper: #ffffff;
    --paper-2: #f6f8fc;
    --carbon: #243041;
    --muted: #6b7585;
    --hot: #e09a3a;
  }
  body {
    background:
      radial-gradient(circle at 10% 0%, #ffffff 0%, transparent 28%),
      radial-gradient(circle at 90% 8%, rgba(var(--theme-rgb),.06) 0%, transparent 24%),
      #f3f5f9;
  }
  .toolbar {
    background: rgba(255, 255, 255, .96);
    border-bottom: 1px solid #e4e8ef;
    box-shadow: 0 4px 18px rgba(36,48,65,.06);
    color: #243041;
  }
  .toolbar .hint, .toolbar a { color: #6b7585; }
  .toolbar a:hover { color: var(--theme); }
  .btn {
    background: var(--theme); border-radius: 8px; box-shadow: none;
    font-weight: 700;
  }
  .frame { background: #f0f3f8; }

  /* 封面：浅色清爽海报 */
  .panel-cover {
    background:
      linear-gradient(165deg, #ffffff 0%, #f8fbff 42%, var(--theme-soft) 100%);
    border: 1px solid #e2e8f4;
    border-radius: 16px;
    color: var(--carbon);
    box-shadow: 0 18px 44px rgba(var(--theme-rgb),.08);
  }
  .panel-cover::after {
    content: ""; position: absolute; left: 52px; right: 52px; top: 122px;
    height: 1px; background: linear-gradient(90deg, var(--theme), var(--theme-2), transparent);
  }
  .grid-bg {
    opacity: 1;
    background-image:
      linear-gradient(rgba(var(--theme-rgb),.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(var(--theme-rgb),.04) 1px, transparent 1px);
    background-size: 48px 48px;
  }
  .glow-a {
    background: radial-gradient(circle, rgba(var(--theme-rgb),.12), transparent 68%);
  }
  .glow-b {
    background: radial-gradient(circle, rgba(var(--theme2-rgb),.1), transparent 70%);
  }
  .cover-wm {
    left: auto; right: -24px; top: 47%; transform: none;
    color: transparent; -webkit-text-stroke: 2px rgba(var(--theme-rgb),.06);
    font-size: 390px; letter-spacing: -.04em;
  }
  .cover-brand .brand-title .en, .cover-title, .mod-line .meta .cn { color: var(--carbon); }
  .cover-brand .brand-title .cn, .cover-brand .brand-no .tag,
  .mod-line .meta .en, .cover-footer .slogan { color: var(--muted); }
  .cover-brand .brand-no .num { color: var(--theme); }
  .kicker {
    background: var(--theme-soft); border: 1px solid rgba(var(--theme-rgb),.14);
    color: var(--theme-deep); border-radius: 6px; padding: 8px 14px;
  }
  .kicker .dot { background: var(--theme-2); }
  .mod-line .n {
    background: linear-gradient(135deg, var(--theme) 0%, var(--theme-2) 90%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }
  .mod-line .meta { border-image: linear-gradient(180deg, var(--theme), var(--theme-2)) 1; }
  .cover-title {
    max-width: 590px; font-size: 67px; line-height: 1.14;
    margin-top: 36px; text-wrap: balance;
  }
  .cover-en { color: var(--theme); font-weight: 700; }
  .cover-rule { background: linear-gradient(90deg, var(--theme), var(--theme-2)); width: 124px; }
  .cover-line {
    color: #4f5d6f; border-left-color: var(--theme-2);
    max-width: 560px; line-height: 1.8;
  }
  .cover-foot-divider { background: #e4e8ef; }
  .cover-footer .dots i { background: #d8dee8; }
  .cover-footer .dots i.active { background: var(--theme); }

  /* 串讲页：纯白卡片 + 清晰时间线 */
  .panel {
    background: var(--paper); border: 1px solid #e4e8ef; border-radius: 16px;
    padding: 36px 40px 26px;
    box-shadow: 0 14px 40px rgba(var(--theme-rgb),.06);
  }
  .panel::before { width: 7px; background: linear-gradient(180deg, var(--theme), var(--theme-2)); }
  .panel-bg .grid {
    background-image:
      linear-gradient(rgba(39,48,68,.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(39,48,68,.025) 1px, transparent 1px);
  }
  .panel-bg .dots {
    background-image: radial-gradient(rgba(var(--theme-rgb),.28) 2px, transparent 2px);
  }
  .panel-bg .arcs { border-color: rgba(var(--theme2-rgb),.1); }
  .brand-title .en, .mod-head .cn, .node .q { color: var(--carbon); }
  .brand-title .cn, .brand-no .tag, .mod-kicker .cat, .sec-lbl, .pager { color: var(--muted); }
  .brand-no .num, .lead b, .pager b { color: var(--theme); }
  .divider {
    background: #e8ecf2;
    margin: 18px 0 20px;
  }
  .mod-head {
    margin-bottom: 20px;
    padding-bottom: 18px;
    border-bottom-color: #eef1f6;
  }
  .mod-head::after { background: linear-gradient(90deg, var(--theme), var(--theme-2)); }
  .mod-kicker .idx { background: var(--theme); border-radius: 4px; }
  .mod-kicker .range { color: var(--theme-deep); background: var(--theme-soft); }

  /* 主线卡：标题与正文分层，正文使用完整横向宽度 */
  .lead {
    position: relative;
    margin: 0 0 22px;
    padding: 16px 19px 18px;
    overflow: hidden;
    background:
      linear-gradient(105deg, rgba(var(--theme-rgb),.08), rgba(var(--theme2-rgb),.035) 72%),
      #fbfdff;
    border: 1px solid rgba(var(--theme-rgb),.14);
    border-radius: 11px;
  }
  .lead::after {
    content: "";
    position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
    background: linear-gradient(180deg, var(--theme), var(--theme-2));
  }
  .lead .mark {
    position: absolute; left: 19px; top: 15px;
    width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 8px;
    background: var(--theme);
    color: transparent;
    font-size: 0; font-style: normal;
    box-shadow: 0 5px 12px rgba(var(--theme-rgb),.16);
  }
  .lead .mark::before {
    content: "↗";
    color: #fff; font-family: Arial, sans-serif;
    font-size: 17px; line-height: 1; font-weight: 700;
  }
  .lead .lbl {
    min-height: 32px;
    display: flex; align-items: center;
    margin: 0 0 10px; padding-left: 46px;
    color: var(--theme-deep);
    font-size: 12px; font-weight: 800; letter-spacing: 2.2px;
  }
  .lead p {
    color: #4f5d6f;
    font-size: 16px; line-height: 1.75;
    text-align: left;
  }
  .lead p b {
    color: var(--theme-deep);
    font-weight: 750;
    background: rgba(var(--theme-rgb),.08);
    padding: 1px 4px; border-radius: 4px;
  }
  .sec-lbl { margin-bottom: 12px; font-size: 12px; }
  .mod-head .cn { font-size: 34px; }
  .node {
    gap: 22px;
    padding: 14px 0;
  }
  .node .content { padding: 18px 20px; }
  .node .q { font-size: 19px; line-height: 1.45; }
  .node .a { font-size: 16.2px; line-height: 1.68; }
  .node .a code { font-size: 15px; }
  .quote p { font-size: 15.5px; line-height: 1.65; }
  .tl::before { background: linear-gradient(180deg, var(--theme), var(--theme-2)); }
  .tl::after {
    background: var(--theme);
    box-shadow: 0 0 0 4px rgba(var(--theme-rgb),.18);
  }
  .tl-end {
    background: var(--theme-2);
    box-shadow: 0 0 0 4px rgba(var(--theme2-rgb),.18);
  }
  .node .dot {
    background: var(--theme); border-radius: 10px;
    box-shadow: 0 0 0 5px var(--paper), 0 5px 14px rgba(var(--theme-rgb),.25);
  }
  .node .content {
    background: #f9fbfe; border-color: #e8ecf2;
    border-radius: 10px; box-shadow: 0 2px 10px rgba(var(--theme-rgb),.04);
  }
  .node .content::before { background: #f9fbfe; border-color: #e8ecf2; }
  .node .a { color: #525a68; }
  .node .a code { color: var(--theme-deep); background: var(--theme-soft); }
  .node.hot .dot {
    background: var(--hot);
    box-shadow: 0 0 0 5px var(--paper), 0 5px 14px rgba(224,138,46,.25);
  }
  .node.hot .content { background: #fff8ee; border-color: #f0dcc0; }
  .node.hot .content::before { background: #fff8ee; border-color: #f0dcc0; }
  .node .hot-badge { background: var(--hot); }
  .quote {
    color: var(--theme-deep); background: var(--theme-soft);
    border-left-color: var(--theme); border-radius: 0 8px 8px 0;
    margin-top: 18px;
    padding: 14px 18px;
  }
  .quote .ico { background: var(--theme); border-radius: 8px; }
  .quote p { color: var(--theme-deep); }
  .foot-divider { background: linear-gradient(90deg, var(--theme), var(--theme-2) 40%, transparent 75%); }
  .footer .deco i.dot { background: var(--theme); }
  .footer .deco i.dot2 { background: var(--theme-2); }
"""

TEMPLATE = (
    A_TEMPLATE
    # 顶部提示 & 返回链接指向 B 版目录
    .replace("模块 __NO__ · __CN__", "第 __NO__ 幕 · __CN__")
    .replace("模块 __NO__ __CN__", "第 __NO__ 幕 · __CN__")
    .replace("导出本主题全部页", "导出本幕全部页")
    .replace('<a href="index.html">← 返回总目录</a>',
             '<a href="index-b.html">← 返回方案B目录</a>')
    # 封面数字：更宽的几何无衬线
    .replace('<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>',
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Russo+One&family=Chakra+Petch:wght@700&display=swap" />\n'
             '<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>')
    .replace("    --line: #e8eaef;\n  }",
             "    --line: #e8eaef;\n"
             "    --cover-num-font: \"Russo One\", \"Chakra Petch\", \"Quantico\", \"Square721 BT\", "
             "\"Arial Black\", sans-serif;\n  }")
    .replace(
        ".cover-wm {\n"
        "    position: absolute; left: 50%; top: 54%; transform: translate(-50%, -50%);\n"
        "    font-size: 440px; line-height: 1; font-weight: 800; font-style: italic;\n"
        "    letter-spacing: -14px; color: rgba(61, 90, 254, .045);",
        ".cover-wm {\n"
        "    position: absolute; left: 50%; top: 54%; transform: translate(-50%, -50%);\n"
        "    font-family: var(--cover-num-font);\n"
        "    font-size: 420px; line-height: 1; font-weight: 400; font-style: normal;\n"
        "    letter-spacing: .02em; color: rgba(61, 90, 254, .045);",
    )
    .replace(
        ".cover-brand .brand-no .num { font-size: 26px; font-weight: 800; color: var(--blue-deep); letter-spacing: 1px; }",
        ".cover-brand .brand-no .num {\n"
        "    font-family: var(--cover-num-font); font-size: 28px; font-weight: 400;\n"
        "    color: var(--blue-deep); letter-spacing: .04em;\n"
        "  }",
    )
    .replace(
        "  .mod-line .n {\n"
        "    font-family: \"Square721 BT\", \"Bank Gothic\", \"Eurostile Extended\", \"Agency FB\", \"Michroma\", sans-serif;\n"
        "    font-size: 132px; line-height: .84; font-weight: 700; font-style: italic; letter-spacing: .02em;",
        "  .mod-line .n {\n"
        "    font-family: var(--cover-num-font);\n"
        "    font-size: 132px; line-height: .84; font-weight: 400; font-style: normal; letter-spacing: .04em;",
    )
    # 封面：品牌副标题 / kicker 带上篇名 / 编号前缀 M -> 无
    .replace("主题总结 · TOPIC RECAP", "追问链叙事 · STORYLINE")
    .replace("TOPIC SUMMARY · 主题串讲", "STORYLINE · ' + TOPIC.part_short + '")
    .replace('">M\' + TOPIC.no', '">\' + TOPIC.no')
    # 封面 mod-line：MODULE / CARD range -> ACT no / part
    .replace('<div class="cn">MODULE</div><div class="en">CARD \' + TOPIC.range',
             '<div class="cn">ACT \' + TOPIC.no + \'</div><div class="en">\' + TOPIC.range')
    # 串讲页表头：no / 10 -> no / 15
    .replace("' + TOPIC.no + ' / 10</div>", "' + TOPIC.no + ' / %d</div>" % TOTAL_ACTS)
    # 串讲页 mod-kicker：MODULE -> ACT，去掉 CARD 前缀（改显示篇名）
    .replace('<span class="idx">MODULE \' + TOPIC.no', '<span class="idx">ACT \' + TOPIC.no')
    .replace('<span class="range">CARD \' + TOPIC.range', '<span class="range">\' + TOPIC.range')
    # B 版独立视觉系统；方案 A 不受影响
    .replace("</style>", B_THEME_CSS + "\n</style>", 1)
    # 每一篇由 payload 注入不同强调色
    .replace(
        "var TOPIC = __TOPIC_JSON__;",
        "var TOPIC = __TOPIC_JSON__;\n"
        "document.documentElement.style.setProperty('--theme', TOPIC.theme.accent);\n"
        "document.documentElement.style.setProperty('--theme-2', TOPIC.theme.accent2);\n"
        "document.documentElement.style.setProperty('--theme-soft', TOPIC.theme.soft);\n"
        "document.documentElement.style.setProperty('--theme-deep', TOPIC.theme.deep);\n"
        "document.documentElement.style.setProperty('--theme-rgb', TOPIC.theme.rgb);\n"
        "document.documentElement.style.setProperty('--theme2-rgb', TOPIC.theme.rgb2);"
    )
    .replace(".replace(/\\{c1\\}/g, '#4c6ef5')", ".replace(/\\{c1\\}/g, TOPIC.theme.accent)")
    .replace(".replace(/\\{c2\\}/g, '#3b5bdb')", ".replace(/\\{c2\\}/g, TOPIC.theme.deep)")
    .replace(".replace(/\\{c3\\}/g, '#6f8dfb')", ".replace(/\\{c3\\}/g, TOPIC.theme.accent2)")
    .replace("backgroundColor: '#e9ebf0'", "backgroundColor: '#f0f3f8'")
)

# ---------------------------------------------------------------------------
# 4. 方案 B 目录页
# ---------------------------------------------------------------------------
INDEX_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>C++ 面试口袋卡片 · 方案B 追问链叙事目录</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
    background:
      radial-gradient(circle at 8% 0%, #ffffff 0%, transparent 26%),
      #f3f5f9;
    color: #243041; padding: 44px 20px 72px;
  }
  .wrap { max-width: 1120px; margin: 0 auto; }
  .head {
    position: relative; overflow: hidden;
    background: linear-gradient(165deg, #ffffff 0%, #f8fbff 48%, #eef1fb 100%);
    border: 1px solid #e2e8f4;
    border-radius: 16px; padding: 46px 48px 44px; margin-bottom: 14px;
    box-shadow: 0 16px 40px rgba(59,91,219,.08); color: #243041;
  }
  .head::before {
    content: "01 — 15"; position: absolute; right: -12px; top: -38px;
    font-size: 154px; line-height: 1; font-weight: 900; letter-spacing: -.08em;
    color: transparent; -webkit-text-stroke: 2px rgba(59,91,219,.07);
    pointer-events: none;
  }
  .head::after {
    content: ""; position: absolute; left: 48px; right: 48px; bottom: 0; height: 4px;
    background: __ARC_GRADIENT__;
  }
  .head .k { font-size: 11px; letter-spacing: 4px; color: #3b5bdb; font-weight: 800; }
  .head h1 { position: relative; margin-top: 18px; font-size: 40px; letter-spacing: .5px; }
  .head p {
    position: relative; margin-top: 16px; max-width: 900px;
    font-size: 15px; line-height: 1.9; color: #5a6573;
  }
  .head .switch { position: relative; margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap; }
  .head .switch a {
    display: inline-block; font-size: 13px; font-weight: 700; letter-spacing: 1px;
    text-decoration: none; color: #3b5bdb; border: 1px solid #d6def5;
    background: #ffffff; padding: 9px 15px; border-radius: 8px;
  }
  .part {
    margin-top: 34px; --theme: #3b5bdb; --theme2: #2746b0;
    --soft: #eef1fb; --deep: #1e3266;
  }
  .part-head {
    display: grid; grid-template-columns: auto auto 1fr; align-items: baseline;
    gap: 14px; margin-bottom: 14px; padding: 0 4px;
  }
  .part-head .cn { font-size: 23px; font-weight: 900; letter-spacing: .5px; }
  .part-head .en { font-size: 11px; letter-spacing: 3px; color: var(--theme); font-weight: 800; }
  .part-head .rule {
    height: 1px; align-self: center;
    background: linear-gradient(90deg, var(--theme), transparent 78%);
  }
  .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 15px; }
  a.card {
    display: grid; grid-template-columns: 72px 1fr; column-gap: 18px;
    text-decoration: none; color: inherit;
    background: #ffffff; border: 1px solid #e4e8ef; border-radius: 12px;
    padding: 22px 24px 22px 18px; position: relative; overflow: hidden;
    transition: transform .15s ease, box-shadow .15s ease;
  }
  a.card::before {
    content: attr(data-no); grid-row: 1 / span 5;
    display: flex; align-items: flex-start; justify-content: center;
    padding-top: 1px; border-right: 1px solid #e8ecf2;
    font-size: 36px; line-height: 1; font-weight: 900; letter-spacing: -.04em;
    color: var(--theme);
  }
  a.card::after {
    content: ""; position: absolute; left: 0; top: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, var(--theme), var(--theme2));
  }
  a.card:hover {
    transform: translateY(-3px);
    border-color: rgba(var(--rgb),.35);
    box-shadow: 0 12px 28px rgba(var(--rgb),.08);
  }
  .card .no { font-size: 10px; letter-spacing: 1.6px; color: #8a8f9b; font-weight: 800; }
  .card h2 { margin-top: 7px; font-size: 21px; letter-spacing: .2px; line-height: 1.3; }
  .card .en { margin-top: 5px; font-size: 10px; letter-spacing: 1.8px; color: var(--theme); font-weight: 800; }
  .card .line { margin-top: 11px; font-size: 13.5px; line-height: 1.65; color: #555c69; }
  .card .foot { margin-top: 13px; display: flex; gap: 8px; flex-wrap: wrap; }
  .tag {
    font-size: 10px; letter-spacing: 1px; padding: 5px 9px; border-radius: 4px;
    background: var(--soft); color: var(--deep); font-weight: 800;
  }
  .tag.gold { background: #faf0e0; color: #9a6a28; }
  @media (max-width: 760px) {
    body { padding: 18px 12px 44px; }
    .head { padding: 34px 26px 32px; }
    .head::after { left: 26px; right: 26px; }
    .head h1 { font-size: 30px; }
    .grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
  <div class="wrap">
    <div class="head">
      <div class="k">STORYLINE EDITION · 追问链叙事版</div>
      <h1>C++ 面试口袋卡片 · 方案B 总结</h1>
      <p>同样 86 题，换一种组织：不按知识分类，而按<b>一个对象从生到死</b>——四篇、十五幕。贯穿例子是一条 LogMessage：诞生、身份、复制转移、进容器、被泛化、被操作、被并发访问、死亡；篇二、篇三把镜头拉远到指令、进程、网络和存储，终章装回一台能跑的机器。每张卡片仍标注原始卡号（001–086），方便与方案A对照。</p>
      <div class="switch"><a href="index.html">← 切换到方案A（按知识主题分 10 个 topic）</a><a href="index-oral.html">口述稿卡片 →</a></div>
    </div>
__PARTS__
  </div>
</body>
</html>
"""


def build():
    # ---- 生成每一幕的 HTML ----
    for a in ACTS:
        items = [CARD[c] for c in a["cards"]]
        payload = {
            "slug": a["slug"], "no": a["no"], "cn": a["cn"], "en": a["en"],
            "range": a["part"], "part_short": PART_SHORT[a["part"]],
            "line": a["line"], "thread": a["thread"],
            "quote": a["quote"], "items": items,
            "theme": PART_THEME[a["part"]],
        }
        html = (TEMPLATE
                .replace("__TOPIC_JSON__", json.dumps(payload, ensure_ascii=False))
                .replace("__PER_PAGE__", str(B_PER_PAGE))
                .replace("__FIRST_PAGE_MAX__", str(a.get("first_page", B_FIRST_PAGE)))
                .replace("__NO__", a["no"])
                .replace("__CN__", a["cn"]))
        with open(os.path.join(HERE, a["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(html)
        pages = b_page_count(len(items), a.get("first_page"))
        print("生成 %-24s  %2d 题 → %d 页" % (a["slug"] + ".html", len(items), pages))

    # ---- 生成 index-b.html（按篇分组）----
    parts_html = []
    i = 0
    while i < len(ACTS):
        part = ACTS[i]["part"]
        part_en = ACTS[i]["part_en"]
        theme = PART_THEME[part]
        group = [a for a in ACTS if a["part"] == part]
        cards = []
        for a in group:
            items = [CARD[c] for c in a["cards"]]
            hot = sum(1 for it in items if it[3])
            pages = b_page_count(len(items), a.get("first_page"))
            cards.append(
                '        <a class="card" data-no="%s" href="%s.html">\n'
                '          <div class="no">ACT %s · %s</div>\n'
                '          <h2>%s</h2>\n'
                '          <div class="en">%s</div>\n'
                '          <div class="line">%s</div>\n'
                '          <div class="foot"><span class="tag">%d 题 / %d 页</span>'
                '<span class="tag gold">%d 个高频</span></div>\n'
                '        </a>' % (a["no"], a["slug"], a["no"], part_en, a["cn"], a["en"],
                                  a["line"], len(items), pages, hot)
            )
        parts_html.append(
            '    <div class="part" style="--theme:%s;--theme2:%s;--soft:%s;--deep:%s;--rgb:%s">\n'
            '      <div class="part-head"><span class="cn">%s</span>'
            '<span class="en">%s</span><span class="rule"></span></div>\n'
            '      <div class="grid">\n%s\n      </div>\n'
            '    </div>' % (
                theme["accent"], theme["accent2"], theme["soft"], theme["deep"], theme["rgb"],
                part, part_en, "\n".join(cards),
            )
        )
        i += len(group)

    with open(os.path.join(HERE, "index-b.html"), "w", encoding="utf-8") as f:
        f.write(INDEX_TEMPLATE.replace("__ARC_GRADIENT__", ARC_GRADIENT)
                              .replace("__PARTS__", "\n".join(parts_html)))
    print("生成 index-b.html")

    # ---- 完整性校验：确保 86 题全部用到且不重复 ----
    used = [c for a in ACTS for c in a["cards"]]
    assert len(used) == len(set(used)), "有重复卡号！"
    missing = sorted(set(CARD) - set(used))
    extra = sorted(set(used) - set(CARD))
    assert not missing, "漏掉卡号: %s" % missing
    assert not extra, "多出卡号: %s" % extra
    print("校验通过：%d 题全部编排、无重复无遗漏" % len(used))

    # ---- 清理旧 slug 的 HTML（幕号重排后遗留）----
    keep = {a["slug"] + ".html" for a in ACTS}
    keep.add("index-b.html")
    for name in os.listdir(HERE):
        if name.startswith("b-act-") and name.endswith(".html") and name not in keep:
            os.remove(os.path.join(HERE, name))
            print("删除旧文件 %s" % name)


if __name__ == "__main__":
    build()
