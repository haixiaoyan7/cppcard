#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C++ 面试口袋卡片 · 分主题总结页生成器

用法:
    python3 _gen_summary.py

产出:
    cppcard/000-summary/topic-01-memory.html   （封面页 + N 个串讲页，自动分页）
    ...
    cppcard/000-summary/index.html             （总目录）

维护方式:
    只改下面的 TOPICS 数据即可，样式与分页逻辑由模板统一控制。
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# 每页放几条考点（超出自动翻到下一页）
PER_PAGE = 7

# ---------------------------------------------------------------------------
# 数据：10 个主题
#   slug    输出文件名
#   no      模块编号
#   cn/en   主题名
#   range   题号区间
#   line    封面一句话总结（主线）
#   thread  串讲页顶部的主线段落（可含 <b>）
#   quote   面试金句
#   items   [题号, 题目, 一句话回答, 是否高频]
# ---------------------------------------------------------------------------
TOPICS = [
    {
        "slug": "topic-01-memory",
        "no": "01",
        "cn": "指针与内存管理",
        "en": "POINTER & MEMORY",
        "range": "001 - 008",
        "line": "一切内存问题，本质都是「谁拥有它，谁在什么时候释放它」。",
        "thread": "本模块的主线是 <b>所有权与生命周期</b>：从裸指针的手动管理，到 <b>RAII</b> 把释放绑定到对象析构，"
                  "再到智能指针把 RAII 模板化。抓住「所有权」这条线，内存泄漏、悬垂指针、双重释放三类 bug 就有了统一解释。",
        "quote": "回答任何内存题，先抛出「所有权 + 生命周期」这条主线，再落到具体语法，面试官立刻判定你有工程经验。",
        "items": [
            ["001", "指针和引用有什么区别？",
             "引用是必须初始化、不可重绑定的别名，无独立地址；指针可空可改，能表达「可选」与所有权转移。", False],
            ["002", "什么是智能指针？",
             "unique_ptr 独占且零开销，shared_ptr 用控制块做引用计数（计数原子、对象访问非线程安全），循环引用用 weak_ptr 打断。", True],
            ["003", "RAII 是什么？还有哪些应用？",
             "构造获取资源、析构释放资源，把清理交给栈展开；不止内存，锁、文件、socket、事务回滚都适用。", False],
            ["004", "栈内存和堆内存的区别？",
             "栈由编译器管理、分配即移指针、容量小且随作用域回收；堆手动/智能指针管理、可变大小、有分配器开销与碎片。", False],
            ["005", "new/delete 与 malloc/free 的区别？",
             "new 额外负责调用构造函数、返回带类型指针、失败抛 bad_alloc；malloc 只给裸字节且失败返回 NULL，二者不可混用。", False],
            ["006", "内存泄漏的常见场景与检测？",
             "异常路径提前返回、shared_ptr 循环引用、容器只增不减、忘记释放句柄；用 ASan / Valgrind / tcmalloc heap profiler 定位。", False],
            ["007", "内存对齐是什么？为什么需要？",
             "让成员地址是其大小的整数倍，使 CPU 单次访存取全数据；alignof/alignas 可控，重排成员顺序能减少填充。", True],
            ["008", "placement new 是什么场景用？",
             "在已分配好的内存上只做构造，把「分配」与「构造」解耦；内存池、容器实现、共享内存对象都靠它，需手动调析构。", False],
        ],
    },
    {
        "slug": "topic-02-oop",
        "no": "02",
        "cn": "面向对象",
        "en": "OBJECT ORIENTED",
        "range": "009 - 019",
        "line": "把每道题归类到「编译期决议」还是「运行期决议」，细节就不会混。",
        "thread": "本模块的主线是 <b>绑定时机</b>：虚函数把调用推迟到运行期，代价是一个 vptr 与一次间接跳转；"
                  "而重载、名字隐藏、访问控制、static / explicit 全部是 <b>编译期</b> 规则。两条线分开，追问就不慌。",
        "quote": "被追问细节时，用一句「这是编译期决议还是运行期决议」切入，胜过背诵十条结论。",
        "items": [
            ["009", "虚函数的实现原理（vtable）？",
             "每个多态类一张虚表存函数地址，对象头部存 vptr；调用时查表间接跳转，多继承下有多张表并用 thunk 调整 this。", True],
            ["010", "纯虚函数和抽象类的作用？",
             "纯虚函数只声明契约不给实现，含纯虚的类不可实例化，用来定义接口并强制派生类实现。", False],
            ["011", "菱形继承问题与虚继承？",
             "普通多继承会有重复基类子对象与二义性；virtual 继承让公共基类只有一份，靠虚基类指针定位，布局与构造顺序更复杂。", False],
            ["012", "构造/析构函数能是虚函数吗？",
             "构造不能虚——vptr 此时还没建立；析构在基类必须虚，否则通过基类指针 delete 派生对象是未定义行为。", False],
            ["013", "深拷贝 vs 浅拷贝？Rule of 3/5？",
             "浅拷贝共享指针导致双重释放；持有资源就要同时管好拷贝构造、拷贝赋值、析构（+ 移动两件），或直接 =delete。", False],
            ["014", "RTTI 和 dynamic_cast 的代价？",
             "依赖虚表旁的 type_info 做运行期类型查找，跨继承层级可能遍历，有明显开销；能用 static_cast 或虚函数就别用它。", True],
            ["015", "四种类型转换的区别？",
             "static_cast 编译期相关类型转换、dynamic_cast 运行期安全向下转、const_cast 去常量、reinterpret_cast 重解释比特。", False],
            ["016", "public/protected/private 继承？",
             "决定基类成员在派生类中的最高可见级别：public 是「is-a」，private 是「用其实现」，protected 供继承链内部使用。", False],
            ["017", "重载 / 重写 / 隐藏的区别？",
             "重载同作用域不同参数、编译期选择；重写虚函数同签名、运行期分派；隐藏是派生类同名成员遮蔽基类整组重载。", True],
            ["018", "static 关键字的多种含义？",
             "文件作用域限制内部链接、函数内保持静态存储期、类内属于类而非对象（无 this，可作回调）。", True],
            ["019", "explicit 与隐式类型转换？",
             "explicit 禁止单参构造/转换函数参与隐式转换与拷贝初始化，避免意外构造导致的歧义与性能损失。", True],
        ],
    },
    {
        "slug": "topic-03-modern",
        "no": "03",
        "cn": "现代 C++ 特性",
        "en": "MODERN C++ 11/14/17/20",
        "range": "020 - 031",
        "line": "现代 C++ 干两件事：把拷贝换成移动，把开销搬到编译期。",
        "thread": "本模块的主线是 <b>省掉不必要的代价</b>：右值与移动语义解决所有权转移，拷贝消除让返回值零成本，"
                  "constexpr / Concepts 把计算与检查提前到编译期，协程则把异步状态机交给编译器生成。",
        "quote": "现代特性题的高分套路：先说「解决什么痛点」，再说「代价是什么」，最后给一个你项目里的落地场景。",
        "items": [
            ["020", "左值 vs 右值？移动语义解决什么？",
             "右值是可被安全掏空的临时量；移动语义让资源「转移指针」而非深拷贝，把 O(n) 拷贝降成 O(1)。", True],
            ["021", "std::move 和 std::forward 做了什么？",
             "move 只是无条件转成右值引用的类型转换，真正搬运发生在移动构造里；forward 按模板推导结果保持原值类别。", True],
            ["022", "RVO / NRVO 与拷贝消除？",
             "编译器直接在调用方栈上构造返回对象；C++17 起对纯右值是「保证消除」，对返回局部对象手动 move 反而抑制 NRVO。", True],
            ["023", "异常安全的三种保证与 noexcept？",
             "basic 不泄漏、strong 要么成功要么回到原状、nothrow 不抛；vector 扩容只有移动构造标 noexcept 时才用移动而非拷贝。", True],
            ["024", "lambda 的本质？捕获怎么工作？",
             "编译器生成的匿名闭包类 + operator()；按值捕获存副本、按引用捕获存引用，异步场景引用捕获易悬垂。", True],
            ["025", "std::function 的原理与开销？",
             "类型擦除：用虚调用/函数指针表统一不同可调用体，大对象会堆分配，热路径优先模板或函数指针。", False],
            ["026", "auto / decltype 的推导规则？",
             "auto 按模板参数推导会丢引用和顶层 const；decltype 保留表达式的值类别与引用，decltype(auto) 用于完美返回。", False],
            ["027", "constexpr 和 const 的区别？",
             "const 是「不可修改」，constexpr 是「可在编译期求值」；后者能用于数组维度、模板参数，C++20 起可用于更多场景。", False],
            ["028", "结构化绑定怎么用？",
             "把 pair/tuple/聚合体/数组一次解构为具名变量，配合 auto& 可就地修改，遍历 map 时最常用。", False],
            ["029", "optional / variant / any 各解决什么？",
             "optional 表达「可能没有值」，variant 是类型安全联合，any 存任意类型需 any_cast；用类型代替魔法值与裸 void*。", False],
            ["030", "C++20 Concepts 解决什么痛点？",
             "给模板参数加可命名的约束，把深层实例化错误变成一行「不满足 concept」，并可参与重载决议。", False],
            ["031", "协程的基本原理与场景？",
             "编译器把函数改写成可挂起/恢复的状态机，帧存在堆上；适合高并发 IO，用同步写法表达异步流程。", False],
        ],
    },
    {
        "slug": "topic-04-template",
        "no": "04",
        "cn": "模板与泛型编程",
        "en": "TEMPLATE & GENERIC",
        "range": "032 - 037",
        "line": "把模板看成「编译期的一门语言」：有变量、有分支、有循环。",
        "thread": "本模块的主线是 <b>编译期的控制流</b>：实例化是代码生成，特化是编译期 if，SFINAE / Concepts 是条件筛选，"
                  "变参模板是循环，CRTP 则把多态搬到编译期实现零开销。",
        "quote": "用「编译期的变量（类型）、分支（特化）、循环（变参展开）」这个类比开场，比逐条背语法专业得多。",
        "items": [
            ["032", "函数模板和类模板的实例化过程？",
             "两阶段查找：定义时检查非依赖名，实例化时按实参生成代码；因此模板定义通常必须可见于头文件。", False],
            ["033", "模板特化和偏特化的区别？",
             "全特化给定全部参数的专用实现；类模板可偏特化（部分参数），函数模板只能全特化，偏特化效果靠重载实现。", False],
            ["034", "SFINAE 是什么？enable_if 怎么用？",
             "替换失败不是错误——只把不匹配的候选移出重载集；enable_if 用返回类型/默认模板参数开关重载，C++20 用 requires 更清晰。", False],
            ["035", "可变参数模板怎么展开？",
             "递归展开「头 + 剩余」，或用 C++17 折叠表达式 (f(args), ...) 一次展开，配合 sizeof...(Args) 取参数个数。", False],
            ["036", "模板元编程的基本思路？",
             "用类型和常量在编译期做计算与分派，运行期零成本；代价是编译时间、可读性与错误信息。", False],
            ["037", "CRTP 是什么？",
             "派生类把自身作为模板参数传给基类，基类 static_cast 回派生类调用，实现无虚表的静态多态，适合高性能路径。", False],
        ],
    },
    {
        "slug": "topic-05-stl",
        "no": "05",
        "cn": "STL 与数据结构",
        "en": "STL & DATA STRUCTURE",
        "range": "038 - 044",
        "line": "容器选型的答案永远先看访问模式，因为内存布局决定性能。",
        "thread": "本模块的主线是 <b>内存布局决定性能</b>：vector 连续因而 cache 友好但扩容会失效迭代器；"
                  "map 是红黑树有序 O(log n)，unordered_map 是哈希桶均摊 O(1) 但缓存不友好；SSO 与 allocator 则在和小对象分配作斗争。",
        "quote": "被问「选哪个容器」时，先反问访问模式：查找方式、是否需要有序、插入位置、元素大小——再给结论。",
        "items": [
            ["038", "vector 的扩容策略和迭代器失效？",
             "容量不足时按 1.5x/2x 申请新块并搬迁，均摊 O(1)；扩容后所有迭代器/指针失效，reserve 可预分配规避。", True],
            ["039", "map vs unordered_map 的实现与性能？",
             "map 是红黑树，有序、稳定 O(log n)；unordered_map 是哈希桶，均摊 O(1) 但有 rehash 抖动、冲突退化与缓存不友好。", True],
            ["040", "deque 的底层结构是什么？",
             "中控 map 数组指向多个固定大小缓冲区，两端插入 O(1) 且不失效引用，但随机访问需两次间接、遍历慢于 vector。", False],
            ["041", "STL 迭代器的分类和设计思想？",
             "输入/输出/前向/双向/随机访问五类，用 traits 在编译期分派最优算法实现，是「算法与容器解耦」的黏合剂。", False],
            ["042", "STL 排序为什么是 introsort？",
             "快排为主，递归深度超限转堆排保证最坏 O(n log n)，小区间改插入排序减少开销；sort 不稳定，stable_sort 才稳定。", False],
            ["043", "allocator 的作用和自定义？",
             "把内存分配策略从容器中抽离，可接内存池/共享内存/对齐分配；C++17 起 pmr 让运行期切换分配器更方便。", False],
            ["044", "string 的 SSO 是什么？",
             "短字符串直接存在对象内部缓冲区（libstdc++ 约 15 字节），免去堆分配；超过阈值才转堆，注意 SSO 使 string 的移动并非总是零成本。", False],
        ],
    },
    {
        "slug": "topic-06-concurrency",
        "no": "06",
        "cn": "并发与多线程",
        "en": "CONCURRENCY",
        "range": "045 - 053",
        "line": "共享数据只有三条路：不共享、加锁共享、无锁共享。",
        "thread": "本模块的主线是 <b>如何处理共享数据</b>：不共享（线程局部 / 消息传递）、加锁共享（mutex、条件变量）、"
                  "无锁共享（原子 + memory_order + CAS）。线程池是这套机制的工程封装，死锁是加锁方式的必然副作用。",
        "quote": "并发题按「为什么会错（数据竞争/重排）→ 怎么修（同步原语）→ 代价是什么（切换、cacheline 争用）」三段讲。",
        "items": [
            ["045", "std::thread 的用法与生命周期管理？",
             "线程对象析构前必须 join 或 detach，否则 terminate；推荐用 jthread 或自写 RAII 守卫，注意参数默认按值拷贝。", False],
            ["046", "mutex / lock_guard / unique_lock 的区别？",
             "mutex 是原语，lock_guard 是最轻的 RAII 包装，unique_lock 支持延迟加锁、转移、与条件变量配合，开销略高。", False],
            ["047", "条件变量怎么用？虚假唤醒？",
             "必须在 while（或带谓词的 wait）中检查条件以应对虚假唤醒；改状态时持锁，notify 可在锁外，避免丢失唤醒。", False],
            ["048", "async / future / promise / packaged_task？",
             "promise 写结果、future 取结果、packaged_task 包装可调用体；async 默认策略可能 deferred，返回值不接收会阻塞析构。", False],
            ["049", "原子操作和内存序？",
             "relaxed 只保证原子性不保证顺序，acquire/release 成对建立同步关系，seq_cst 全局单一顺序但最贵。", True],
            ["050", "无锁编程的思路？CAS？",
             "用 compare_exchange 循环替代加锁，失败重试；ABA 用带版本号的指针或 hazard pointer 解决，回收内存是最大难点。", True],
            ["051", "线程池怎么设计？",
             "任务队列 + 工作线程 + 条件变量唤醒；关注队列竞争（分片/work stealing）、优雅退出、任务取消与需保序时的 strand。", True],
            ["052", "互斥锁/读写锁/自旋锁/信号量选型？",
             "临界区极短且不阻塞用自旋，读多写少用读写锁（注意写饥饿），需要计数或跨进程用信号量，其余默认互斥锁。", False],
            ["053", "死锁的四个必要条件与破解？",
             "互斥、持有并等待、不可抢占、循环等待；工程上最实用的是统一全局加锁顺序或用 std::scoped_lock 一次锁多个。", False],
        ],
    },
    {
        "slug": "topic-07-lowlevel",
        "no": "07",
        "cn": "编译链接与底层机制",
        "en": "BUILD & LOW LEVEL",
        "range": "054 - 062",
        "line": "从一行代码到一条指令：符号能否对上，指令跑得多快。",
        "thread": "本模块的主线是 <b>代码的一生</b>：预处理→编译→汇编→链接决定符号从哪来，ODR / ABI / extern \"C\" 决定符号能不能对上；"
                  "运行期则由虚拟内存、页表与 cache 决定这条指令跑得多快。",
        "quote": "「undefined symbol / duplicate symbol 怎么排查」是最实战的问法：答 nm、objdump、-Wl,--verbose 比背概念加分。",
        "items": [
            ["054", "编译的四个阶段？",
             "预处理展开宏与头文件、编译生成汇编、汇编生成含符号表的目标文件、链接完成符号解析与重定位。", False],
            ["055", "静态链接 vs 动态链接？",
             "静态把代码拷进可执行文件，体积大但启动快无依赖；动态运行期加载，靠 PLT/GOT 延迟绑定，省内存但有符号覆盖与版本问题。", True],
            ["056", "违反 ODR 会怎样？",
             "同一实体在多个 TU 中的定义必须完全一致，否则是未定义行为（常表现为诡异崩溃）；inline/模板允许多份但内容须相同。", True],
            ["057", "ABI 兼容性与 extern \"C\"？",
             "ABI 涉及名字修饰、调用约定、对象布局、异常模型；extern \"C\" 关闭名字修饰以供跨语言调用，跨边界接口应只用 POD。", False],
            ["058", "C++ 对象的内存布局？",
             "多态类头部有 vptr，基类子对象按声明顺序排列并考虑对齐填充，空基类优化可使其不占空间。", False],
            ["059", "虚拟内存与地址转换？",
             "每进程独立虚拟地址空间，MMU 经多级页表 + TLB 转物理地址，缺页中断触发按需调页与换页。", True],
            ["060", "内存碎片？分段 vs 分页？",
             "内部碎片来自定长块/对齐，外部碎片来自变长分配空隙；分页定长易管理无外部碎片，分段按逻辑单位但会产生外部碎片。", False],
            ["061", "用户态 vs 内核态？系统调用开销？",
             "权限级别切换需保存恢复上下文，并伴随 cache/TLB 污染与可能的调度；因此有 vDSO、批量 IO、io_uring 这类减少陷入的设计。", True],
            ["062", "cache 友好代码？false sharing？",
             "按行连续访问、结构体紧凑、避免随机指针跳转；多线程写同一 cacheline 会互相失效，用 alignas(64) 隔离热点变量。", True],
        ],
    },
    {
        "slug": "topic-08-design",
        "no": "08",
        "cn": "设计模式与系统设计",
        "en": "PATTERN & SYSTEM DESIGN",
        "range": "063 - 068",
        "line": "模式是用一层间接换可变性；系统设计是用指标证明你的取舍。",
        "thread": "本模块的主线是 <b>用间接层换取可变性</b>：单例控制实例数，工厂隔离构造，观察者解耦通知，PIMPL 隔离编译依赖；"
                  "而日志系统与内存池是把并发、RAII、内存布局综合落地的压轴题。",
        "quote": "系统设计题必须给指标：吞吐、P99 延迟、内存占用，并说明你在哪个维度做了取舍。",
        "items": [
            ["063", "线程安全的单例怎么写？",
             "Meyer's Singleton：函数内 static 局部变量，C++11 保证初始化线程安全且惰性；注意析构顺序与跨动态库多实例问题。", False],
            ["064", "工厂 / 抽象工厂怎么实现？",
             "用 name→creator 的注册表返回 unique_ptr<Base>，把对象创建与使用解耦；抽象工厂生产一族相互配套的产品。", False],
            ["065", "观察者 / 发布-订阅怎么实现？",
             "主题维护订阅者列表并广播事件；用 weak_ptr 或 token 反注册防止悬垂，发布-订阅再加一层消息通道彻底解耦。", False],
            ["066", "PIMPL 解决什么问题？",
             "把私有成员藏进 Impl 指针，隐藏实现、稳定 ABI、切断头文件依赖加快编译；代价是一次间接与一次堆分配。", False],
            ["067", "如何设计高性能日志系统？",
             "前端只做「填二进制/格式化后移」入无锁或双缓冲队列，后端单线程批量落盘；分级、异步刷盘、滚动切分与丢弃策略是要点。", True],
            ["068", "如何设计内存池？",
             "按定长块切分大 chunk，用空闲链表 O(1) 分配释放，配合 placement new 构造；注意对齐、线程本地缓存与归还时机。", True],
        ],
    },
    {
        "slug": "topic-09-net-os",
        "no": "09",
        "cn": "网络编程与操作系统",
        "en": "NETWORK & OS",
        "range": "069 - 077",
        "line": "跟着一次请求的数据流走：网卡 → 内核 → 用户态 → 执行单元。",
        "thread": "本模块的主线是 <b>一次请求的数据流</b>：epoll 告诉你何时可读，Reactor 组织事件分发，零拷贝减少搬运，"
                  "io_uring 连系统调用都省；最后由进程 / 线程 / 协程这三种执行单元去处理。",
        "quote": "把 epoll、Reactor、零拷贝串成「一个连接从 accept 到响应」的完整叙事，一次讲透三道题。",
        "items": [
            ["069", "epoll 的 ET 和 LT 区别？",
             "LT 只要可读就持续通知，编程简单；ET 只在状态变化时通知一次，必须循环读写到返回 EAGAIN，否则漏事件。", True],
            ["070", "select / poll / epoll 的差异？",
             "前两者每次都要全量传入并线性扫描 O(n)；epoll 用红黑树管理 fd、就绪链表返回事件，就绪通知近似 O(1)。", True],
            ["071", "Reactor 模型？",
             "事件循环等待就绪再分发给处理器；主从 Reactor 让 acceptor 与 IO 分离，one loop per thread 避免锁并利于 CPU 亲和。", True],
            ["072", "TCP 三次握手、四次挥手与 TIME_WAIT？",
             "三次是为双向确认序号并防历史连接；四次因 TCP 半关闭；TIME_WAIT 等 2MSL 保证末 ACK 可重传且旧报文消散。", True],
            ["073", "零拷贝与 mmap 的原理？",
             "sendfile/splice 让数据在内核内直达网卡，省去用户态往返；mmap 用页表映射替代 read 拷贝，但有缺页与一致性成本。", True],
            ["074", "io_uring 与惊群问题？",
             "io_uring 用共享 SQ/CQ 环形队列批量提交完成，大幅减少陷入；惊群用 EPOLLEXCLUSIVE 或 SO_REUSEPORT 解决。", False],
            ["075", "进程 / 线程 / 协程的区别？",
             "进程有独立地址空间隔离性最好，线程共享内存切换更轻，协程在用户态由程序自己调度、切换成本最低但需非阻塞配合。", True],
            ["076", "fork 的写时拷贝机制？",
             "父子共享物理页并标只读，任一方写触发缺页再复制该页；fork 在父进程返回子 pid、子进程返回 0 是内核设置不同返回寄存器。", False],
            ["077", "IPC 有哪些方式？如何选？",
             "管道/FIFO 适合流式父子、消息队列适合定长消息、共享内存最快但需自行同步、socket 可跨机、信号只作通知。", False],
        ],
    },
    {
        "slug": "topic-10-database",
        "no": "10",
        "cn": "数据库与分布式",
        "en": "DATABASE & DISTRIBUTED",
        "range": "078 - 086",
        "line": "持久化的两个命题：正确性靠日志与 MVCC，速度靠索引与内存。",
        "thread": "本模块的主线是 <b>正确性与速度的平衡</b>：ACID 由锁 + MVCC + 三大日志共同保证，B+ 树索引决定查询能多快，"
                  "Redis 用内存 + 单线程事件循环把速度推到极限，Raft 则把一致性扩展到多机。",
        "quote": "后端岗必答套路：先问「读写比例和数据量」再展开，比直接背隔离级别定义专业得多。",
        "items": [
            ["078", "ACID 与四种隔离级别？",
             "原子性靠 undo、持久性靠 redo、隔离性靠锁与 MVCC；RU/RC/RR/串行化分别对应脏读、不可重复读、幻读的逐级消除。", True],
            ["079", "InnoDB 的 B+ 树索引？聚簇 vs 非聚簇？",
             "B+ 树只有叶子存数据且叶子成链表利于范围查询；聚簇索引叶子即整行，二级索引叶子存主键需回表。", True],
            ["080", "索引优化：最左前缀 / 覆盖索引 / 回表？",
             "联合索引必须从最左列连续使用；覆盖索引让查询字段都在索引里免回表；对列做函数、隐式类型转换、前导模糊会让索引失效。", True],
            ["081", "undolog / redolog / binlog 的区别？",
             "undo 是逻辑回滚与 MVCC 版本来源，redo 是物理页日志保崩溃恢复，binlog 是 Server 层逻辑日志用于主从与归档，二阶段提交保证一致。", False],
            ["082", "MVCC 的实现原理？",
             "行上的事务 id + 回滚指针构成 undo 版本链，ReadView 按活跃事务集判断可见版本；RC 每条语句建视图，RR 事务内复用。", True],
            ["083", "Raft 算法？为什么不防拜占庭？",
             "分解为 Leader 选举、日志复制、安全性三部分，多数派提交；它假设节点只会宕机不会说谎，故无法应对恶意节点。", False],
            ["084", "Redis 常见结构与缓存一致性？",
             "String/Hash/List/Set/ZSet 各配底层编码（ziplist、skiplist 等）；一致性常用「先更库再删缓存 + 延迟双删」并容忍最终一致。", False],
            ["085", "缓存穿透 / 击穿 / 雪崩？",
             "穿透是查不存在的 key（空值缓存 + 布隆过滤器），击穿是热点 key 过期（互斥重建/逻辑过期），雪崩是大量同时失效（过期时间加随机）。", True],
            ["086", "Redis 为什么快？过期与淘汰策略？",
             "纯内存 + 高效结构 + 单线程免锁 + IO 多路复用；过期用惰性删除加定期抽样，内存满按 maxmemory-policy 走 LRU/LFU/随机淘汰。", True],
        ],
    },
]

# ---------------------------------------------------------------------------
# 模板
# ---------------------------------------------------------------------------
TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>C++ 面试总结 · 模块 __NO__ __CN__ · 9:16</title>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<style>
  :root {
    --blue: #3d5afe;
    --blue-mid: #4c6ef5;
    --blue-deep: #3949ab;
    --blue-soft: #eef1fa;
    --accent: #12b5c9;
    --accent-deep: #0aa2b8;
    --accent-ink: #0b7c8c;
    --accent-bg: #e7fbfd;
    --ink: #1f232c;
    --ink-soft: #4a4f5a;
    --gray: #9aa0ac;
    --panel-bg: #ffffff;
    --page-bg: #e9ebf0;
    --line: #e8eaef;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { min-height: 100%; }
  body {
    font-family: "PingFang SC", "Microsoft YaHei", "Hiragino Sans GB",
      "Helvetica Neue", Arial, sans-serif;
    background: var(--page-bg);
    color: var(--ink);
    -webkit-font-smoothing: antialiased;
    display: flex; flex-direction: column; align-items: center;
    padding: 96px 16px 48px;
  }

  /* ---------- Toolbar ---------- */
  .toolbar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 50;
    display: flex; align-items: center; justify-content: center; gap: 12px;
    padding: 12px 16px;
    background: rgba(24, 28, 44, 0.92);
    backdrop-filter: blur(6px); color: #fff;
  }
  .btn {
    border: none; cursor: pointer;
    background: linear-gradient(135deg, #4c6ef5, #3b5bdb);
    color: #fff; font-size: 14px; font-weight: 600; letter-spacing: 1px;
    padding: 10px 18px; border-radius: 10px;
    box-shadow: 0 6px 16px rgba(61, 90, 254, 0.4);
    transition: transform .15s ease;
  }
  .btn:hover { transform: translateY(-1px); }
  .btn.ghost { background: rgba(255,255,255,0.12); box-shadow: none; }
  .btn:disabled { opacity: .6; cursor: default; }
  .hint { font-size: 12px; color: #b9c0d6; }
  .toolbar a { color: #b9c0d6; font-size: 12px; text-decoration: none; }
  .toolbar a:hover { color: #fff; }

  /* ---------- Canvas ---------- */
  .pages { display: flex; flex-direction: column; align-items: center; gap: 26px; }
  .viewport { overflow: hidden; }
  .stage { transform-origin: top left; }
  .frame { width: 720px; height: 1280px; background: var(--page-bg); padding: 20px; }

  /* ================= 封面页（浅色渐变，轻盈但与单题卡片有区分） ================= */
  .panel-cover {
    position: relative; width: 100%; height: 100%;
    background: linear-gradient(165deg, #ffffff 0%, #f4f7ff 42%, #e8eefc 100%);
    border: 1px solid #dfe5f4; border-radius: 22px;
    padding: 46px 52px 38px;
    display: flex; flex-direction: column; overflow: hidden;
    color: var(--ink);
    box-shadow: 0 18px 44px rgba(40, 55, 100, .10);
  }
  .grid-bg {
    position: absolute; inset: 0; pointer-events: none;
    background-image:
      linear-gradient(rgba(61,90,254,.045) 1px, transparent 1px),
      linear-gradient(90deg, rgba(61,90,254,.045) 1px, transparent 1px);
    background-size: 60px 60px;
  }
  .glow-a, .glow-b { position: absolute; border-radius: 50%; pointer-events: none; }
  .glow-a {
    width: 620px; height: 620px; top: -230px; right: -200px;
    background: radial-gradient(circle, rgba(93,125,246,.22) 0%, rgba(93,125,246,0) 68%);
  }
  .glow-b {
    width: 520px; height: 520px; bottom: -240px; left: -180px;
    background: radial-gradient(circle, rgba(18,181,201,.2) 0%, rgba(18,181,201,0) 70%);
  }
  .cover-wm {
    position: absolute; left: 50%; top: 54%; transform: translate(-50%, -50%);
    font-size: 440px; line-height: 1; font-weight: 800; font-style: italic;
    letter-spacing: -14px; color: rgba(61, 90, 254, .045);
    pointer-events: none; user-select: none;
  }
  .panel-cover > .layer { position: relative; z-index: 1; }

  .cover-brand { display: flex; align-items: center; gap: 16px; }
  .cover-brand .brand-title .en { font-size: 20px; font-weight: 700; letter-spacing: 1.5px; color: var(--ink); }
  .cover-brand .brand-title .cn { margin-top: 4px; font-size: 13px; color: var(--gray); letter-spacing: 3px; }
  .cover-brand .brand-no { text-align: right; }
  .cover-brand .brand-no .num { font-size: 26px; font-weight: 800; color: var(--blue-deep); letter-spacing: 1px; }
  .cover-brand .brand-no .tag { margin-top: 4px; font-size: 12px; color: var(--gray); letter-spacing: 2px; }

  .cover-hero { flex: 1; display: flex; flex-direction: column; justify-content: center; padding-bottom: 12px; }
  .kicker {
    align-self: flex-start; display: inline-flex; align-items: center; gap: 10px;
    background: rgba(18, 181, 201, .1);
    border: 1px solid rgba(10, 162, 184, .34); color: var(--accent-ink);
    font-size: 13px; font-weight: 700; letter-spacing: 4px;
    padding: 9px 20px; border-radius: 999px; margin-bottom: 40px;
  }
  .kicker .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent-deep); }
  .mod-line { display: flex; align-items: stretch; gap: 16px; }
  .mod-line .n {
    font-family: "Square721 BT", "Bank Gothic", "Eurostile Extended", "Agency FB", "Michroma", sans-serif;
    font-size: 132px; line-height: .84; font-weight: 700; font-style: italic; letter-spacing: .02em;
    padding: 0 .16em 0 .06em;
    background: linear-gradient(135deg, #3949ab 0%, #4c8ff0 50%, #38c6d6 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }
  .mod-line .meta {
    position: relative;
    display: flex; flex-direction: column; justify-content: flex-end;
    padding: 8px 0 16px 16px;
  }
  .mod-line .meta::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    border-radius: 2px;
    background: linear-gradient(180deg, #4c8ff0, #38c6d6);
  }
  .mod-line .meta .cn { font-size: 22px; font-weight: 800; color: var(--ink); letter-spacing: 2px; }
  .mod-line .meta .en { margin-top: 7px; font-size: 12.5px; color: var(--gray); letter-spacing: 2px; }
  .cover-title { font-size: 64px; font-weight: 800; line-height: 1.22; color: var(--ink); margin: 28px 0 16px; letter-spacing: 1px; }
  .cover-en { font-size: 15px; letter-spacing: 5px; color: #9aa4c4; margin-bottom: 30px; }
  .cover-rule { width: 92px; height: 4px; border-radius: 2px; background: linear-gradient(90deg, var(--accent-deep), rgba(18,181,201,0)); margin-bottom: 26px; }
  .cover-line {
    font-size: 23px; line-height: 1.72; color: var(--ink-soft); font-weight: 500;
    border-left: 3px solid var(--accent); padding-left: 20px;
  }
  .cover-foot-divider { height: 1px; background: #dfe4f0; margin: 30px 0 16px; }
  .cover-footer { display: flex; align-items: center; justify-content: space-between; }
  .cover-footer .slogan { font-size: 12px; color: var(--gray); letter-spacing: 3px; }
  .cover-footer .dots { display: flex; gap: 9px; }
  .cover-footer .dots i { width: 9px; height: 9px; border-radius: 50%; background: #d3d7e0; display: block; }
  .cover-footer .dots i.active { background: var(--accent); }

  /* ================= 串讲页（原表头 + 时间线） ================= */
  .panel {
    position: relative; width: 100%; height: 100%;
    background: var(--panel-bg); border: 1px solid #e2e5ec; border-radius: 22px;
    padding: 32px 38px 22px;
    display: flex; flex-direction: column; overflow: hidden;
    box-shadow: 0 18px 44px rgba(40, 55, 100, .10);
  }
  .panel::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 8px;
    background: linear-gradient(180deg, #4c6ef5, #3b5bdb 55%, #12b5c9);
    z-index: 2;
  }
  /* 背景装饰层：淡网格 + 圆点阵 + 同心弧 */
  .panel-bg { position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
  .panel-bg .grid {
    position: absolute; inset: 0;
    background-image:
      linear-gradient(rgba(76,110,245,.035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(76,110,245,.035) 1px, transparent 1px);
    background-size: 54px 54px;
    -webkit-mask-image: radial-gradient(120% 90% at 100% 0%, #000 30%, transparent 72%);
    mask-image: radial-gradient(120% 90% at 100% 0%, #000 30%, transparent 72%);
  }
  /* 右上角圆点阵 */
  .panel-bg .dots {
    position: absolute; top: 30px; right: 30px;
    width: 132px; height: 96px;
    background-image: radial-gradient(rgba(76,110,245,.22) 2px, transparent 2px);
    background-size: 20px 20px;
    -webkit-mask-image: linear-gradient(225deg, #000 20%, transparent 78%);
    mask-image: linear-gradient(225deg, #000 20%, transparent 78%);
  }
  /* 左下角同心弧 */
  .panel-bg .arcs {
    position: absolute; left: -130px; bottom: -130px;
    width: 260px; height: 260px; border-radius: 50%;
    border: 1px solid rgba(18,181,201,.05);
    box-shadow:
      0 0 0 24px rgba(18,181,201,.03),
      0 0 0 50px rgba(76,110,245,.025);
  }
  .panel > *:not(.panel-bg) { position: relative; z-index: 1; }

  .brand { display: flex; align-items: center; gap: 16px; }
  .logo { width: 52px; height: 52px; flex-shrink: 0; }
  .logo svg { width: 100%; height: 100%; display: block; }
  .brand-title { flex: 1; }
  .brand-title .en { font-size: 19px; font-weight: 700; letter-spacing: 1.5px; }
  .brand-title .cn { margin-top: 4px; font-size: 12.5px; color: var(--gray); letter-spacing: 3px; }
  .brand-no { text-align: right; }
  .brand-no .num { font-size: 25px; font-weight: 800; color: var(--blue-deep); letter-spacing: 1px; }
  .brand-no .tag { margin-top: 4px; font-size: 11.5px; color: var(--gray); letter-spacing: 2px; }
  .divider { height: 1px; background: var(--line); margin: 15px 0 16px; }

  .mod-head {
    position: relative; margin-bottom: 15px;
    padding: 2px 0 14px;
    border-bottom: 2px solid #eef1f6;
  }
  .mod-head::after {
    content: ""; position: absolute; left: 0; bottom: -2px;
    width: 120px; height: 2px;
    background: linear-gradient(90deg, #4c6ef5, #12b5c9);
  }
  .mod-kicker {
    display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
  }
  .mod-kicker .idx {
    font-size: 12px; font-weight: 800; letter-spacing: 1px;
    color: #fff; background: linear-gradient(135deg, #4c6ef5, #3b5bdb);
    padding: 3px 10px; border-radius: 6px;
  }
  .mod-kicker .cat {
    font-size: 10.5px; font-weight: 700; letter-spacing: 3px; color: var(--gray);
  }
  .mod-kicker .range {
    margin-left: auto; font-size: 11.5px; font-weight: 700; letter-spacing: 1px;
    color: var(--accent-ink); background: var(--accent-bg);
    padding: 4px 11px; border-radius: 20px;
  }
  .mod-head .cn {
    font-size: 32px; font-weight: 800; letter-spacing: 1px; color: var(--ink);
    line-height: 1.1;
  }

  /* 主线导语 */
  .lead {
    position: relative; margin-bottom: 16px; padding: 4px 0 4px 42px;
  }
  .lead .mark {
    position: absolute; left: 0; top: -10px;
    font-size: 54px; line-height: 1; font-weight: 800; font-style: italic;
    color: rgba(76,110,245,.18); font-family: Georgia, serif;
  }
  .lead .lbl { font-size: 10px; letter-spacing: 3px; color: var(--blue-deep); font-weight: 700; margin-bottom: 6px; }
  .lead p { font-size: 16px; line-height: 1.72; color: var(--ink-soft); }
  .lead b { color: var(--blue-deep); font-weight: 700; }

  .sec-lbl {
    display: flex; align-items: center; gap: 10px;
    font-size: 10.5px; letter-spacing: 3px; color: var(--gray);
    font-weight: 700; margin-bottom: 6px;
  }
  .sec-lbl::after { content: ""; flex: 1; height: 1px; background: var(--line); }

  /* ---------- 时间线 ---------- */
  .tl {
    flex: 1; min-height: 0; position: relative;
    display: flex; flex-direction: column; gap: 0;
    padding-left: 8px;
  }
  /* 主干渐变轴 + 顶/底端点 */
  .tl::before {
    content: ""; position: absolute; left: 30.5px; top: 10px; bottom: 10px; width: 3px;
    border-radius: 3px;
    background: linear-gradient(180deg, #4c6ef5, #3b8fd6 55%, #12b5c9);
  }
  .tl::after {
    content: ""; position: absolute; left: 26.5px; top: 2px;
    width: 11px; height: 11px; border-radius: 50%;
    background: #4c6ef5; box-shadow: 0 0 0 4px rgba(76,110,245,.18);
  }
  .tl-end {
    position: absolute; left: 26.5px; bottom: 2px;
    width: 11px; height: 11px; border-radius: 50%;
    background: #12b5c9; box-shadow: 0 0 0 4px rgba(18,181,201,.18);
    z-index: 1;
  }

  .node {
    flex: 1; min-height: 0; position: relative;
    display: flex; gap: 20px; align-items: center;
    padding: 9px 0;
  }
  /* 节点之间的过渡装饰：右侧虚线 + 小菱形 */
  .node:not(:last-child)::after {
    content: ""; position: absolute; left: 74px; right: 4px; bottom: -1px;
    height: 1px;
    background-image: repeating-linear-gradient(90deg, #dbe1ee 0 5px, transparent 5px 11px);
    background-size: 11px 1px;
    opacity: .85;
  }
  .node .gap-mark {
    position: absolute; left: calc(50% + 35px); bottom: -6px;
    transform: translateX(-50%) rotate(45deg);
    width: 8px; height: 8px; border-radius: 2px;
    background: #fff; border: 1.5px solid #c7d2f2; z-index: 1;
  }
  .node.hot .gap-mark { border-color: #a9e4ec; }
  /* 节点连接横向小引线 */
  .node .dot {
    position: relative; z-index: 2; flex-shrink: 0;
    width: 48px; height: 48px; border-radius: 50%;
    background: linear-gradient(150deg, #5c7cfa, #3b5bdb);
    color: #fff; font-size: 14px; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 0 5px #fff, 0 5px 14px rgba(59,91,219,.28);
  }
  .node .dot::after {
    content: ""; position: absolute; right: -14px; top: 50%; transform: translateY(-50%);
    width: 14px; height: 2px; background: #d7deee;
  }
  .node .content {
    flex: 1; min-width: 0; position: relative;
    background: #fbfcfe; border: 1px solid #eef1f6;
    border-radius: 12px; padding: 15px 18px;
    box-shadow: 0 2px 8px rgba(40,55,100,.04);
  }
  /* 卡片左侧朝向时间轴的小三角 */
  .node .content::before {
    content: ""; position: absolute; left: -7px; top: 50%; transform: translateY(-50%) rotate(45deg);
    width: 12px; height: 12px; background: #fbfcfe;
    border-left: 1px solid #eef1f6; border-bottom: 1px solid #eef1f6;
  }
  .node .q {
    display: flex; align-items: baseline; gap: 8px;
    font-size: 17.5px; font-weight: 700; color: var(--ink);
    line-height: 1.4; letter-spacing: .2px;
  }
  .node .q .fire { font-size: 14px; margin-left: 3px; }
  .node .a { margin-top: 6px; font-size: 14.8px; line-height: 1.6; color: var(--ink-soft); }
  .node .a code {
    font-family: "SFMono-Regular", "Consolas", "Menlo", monospace;
    font-size: 13.6px; color: var(--ink); background: rgba(61, 90, 254, .08);
    padding: 1px 5px; border-radius: 4px;
  }
  /* 高频题：青绿点缀 + 徽标 */
  .node.hot .dot { background: linear-gradient(150deg, #3fd0de, #0aa2b8); box-shadow: 0 0 0 5px #fff, 0 5px 14px rgba(10,162,184,.3); }
  .node.hot .content { background: #f4fdff; border-color: #d8f2f6; }
  .node.hot .content::before { background: #f4fdff; border-color: #d8f2f6; }
  .node .hot-badge {
    flex-shrink: 0; font-size: 9px; font-weight: 800; letter-spacing: 1px;
    color: #fff; background: var(--accent-deep);
    padding: 2px 7px; border-radius: 20px; align-self: center;
  }

  .quote {
    flex: 0 0 auto; display: flex; align-items: center; gap: 13px;
    background: var(--accent-bg); border-left: 4px solid var(--accent-deep);
    border-radius: 0 12px 12px 0; padding: 12px 16px; margin-top: 12px;
  }
  .quote .ico {
    width: 34px; height: 34px; flex-shrink: 0; border-radius: 50%;
    background: linear-gradient(135deg, #3fd0de, #0aa2b8);
    color: #fff; font-size: 17px; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
  }
  .quote p { font-size: 14px; line-height: 1.6; color: var(--accent-ink); font-weight: 600; }

  .foot-divider {
    height: 2px; margin: 13px 0 11px; border-radius: 2px;
    background: linear-gradient(90deg, #4c6ef5, #12b5c9 40%, transparent 75%);
    opacity: .55;
  }
  .footer { position: relative; display: flex; align-items: center; justify-content: space-between; }
  .footer .slogan { font-size: 11.5px; color: var(--gray); letter-spacing: 3px; }
  .footer .deco {
    position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
    display: flex; align-items: center; gap: 7px;
  }
  .footer .deco i { display: block; height: 4px; border-radius: 2px; background: #dfe4f0; }
  .footer .deco i.s { width: 4px; }
  .footer .deco i.m { width: 16px; }
  .footer .deco i.dot { width: 6px; height: 6px; border-radius: 50%; background: #4c6ef5; }
  .footer .deco i.dot2 { width: 6px; height: 6px; border-radius: 50%; background: #12b5c9; }
  .pager { font-size: 11.5px; color: var(--gray); letter-spacing: 2px; }
  .pager b { color: var(--blue); font-size: 14px; }
</style>
</head>
<body>
  <div class="toolbar" data-html2canvas-ignore="true">
    <button id="exportAll" class="btn">⬇ 导出本主题全部页 (PNG)</button>
    <span class="hint">模块 __NO__ · __CN__ · 720 × 1280 · 2× 高清</span>
    <a href="index.html">← 返回总目录</a>
  </div>

  <div class="pages" id="pages"></div>

<script>
var PER_PAGE = __PER_PAGE__;
var TOPIC = __TOPIC_JSON__;

var LOGO = '<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
  + '<defs><linearGradient id="lg{i}" x1="0" y1="0" x2="1" y2="1">'
  + '<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
  + '<path d="M26 6 H74 A20 20 0 0 1 94 26 V74 A20 20 0 0 1 74 94 H26 L6 74 V26 A20 20 0 0 1 26 6 Z" fill="url(#lg{i})"/>'
  + '<path d="M6 74 L26 94 H16 A10 10 0 0 1 6 84 Z" fill="{c3}"/>'
  + '<path d="M48.6 36.2 A18 18 0 1 0 48.6 63.8" fill="none" stroke="{fg}" stroke-width="9" stroke-linecap="round"/>'
  + '<g fill="{fg}"><rect x="58" y="48" width="12" height="4" rx="1.6"/><rect x="62" y="44" width="4" height="12" rx="1.6"/>'
  + '<rect x="72" y="48" width="12" height="4" rx="1.6"/><rect x="76" y="44" width="4" height="12" rx="1.6"/></g></svg>';

function logo(i) {
  return LOGO.replace(/\{i\}/g, i)
    .replace(/\{c1\}/g, '#4c6ef5')
    .replace(/\{c2\}/g, '#3b5bdb')
    .replace(/\{c3\}/g, '#6f8dfb')
    .replace(/\{fg\}/g, '#ffffff');
}

/* ---- 分页：第一张串讲页（含主线导语）最多 FIRST_CAP 条，其余页按 PER_PAGE 均分 ---- */
var FIRST_CAP = __FIRST_PAGE_MAX__;
var n = TOPIC.items.length;
var chunks = [];
var cursor = 0;
if (FIRST_CAP > 0 && n > FIRST_CAP) {
  chunks.push(TOPIC.items.slice(0, FIRST_CAP));
  cursor = FIRST_CAP;
}
var rest = n - cursor;
if (rest > 0) {
  var pageCount = Math.max(1, Math.ceil(rest / PER_PAGE));
  for (var p = 0; p < pageCount; p++) {
    var size = Math.ceil((n - cursor) / (pageCount - p));
    chunks.push(TOPIC.items.slice(cursor, cursor + size));
    cursor += size;
  }
}
if (!chunks.length) chunks.push([]);
var totalPages = chunks.length + 1; // 含封面

var pagesEl = document.getElementById('pages');

function addPage(name, html) {
  var vp = document.createElement('div');
  vp.className = 'viewport';
  vp.innerHTML = '<div class="stage"><div class="frame" data-name="' + name + '">' + html + '</div></div>';
  pagesEl.appendChild(vp);
}

/* ---- 封面页 ---- */
addPage(TOPIC.slug + '-00-cover',
  '<div class="panel-cover">'
  + '<div class="grid-bg"></div><div class="glow-a"></div><div class="glow-b"></div>'
  + '<div class="cover-wm">' + TOPIC.no + '</div>'
  + '<div class="layer cover-brand">'
  +   '<div class="logo">' + logo('cover') + '</div>'
  +   '<div class="brand-title"><div class="en">C++ INTERVIEW CARD</div><div class="cn">主题总结 · TOPIC RECAP</div></div>'
  +   '<div class="brand-no"><div class="num">M' + TOPIC.no + '</div><div class="tag">' + TOPIC.range + '</div></div>'
  + '</div>'
  + '<div class="layer cover-hero">'
  +   '<div class="kicker"><span class="dot"></span>TOPIC SUMMARY · 主题串讲</div>'
  +   '<div class="mod-line"><div class="n">' + TOPIC.no + '</div>'
  +     '<div class="meta"><div class="cn">MODULE</div><div class="en">CARD ' + TOPIC.range + '</div></div></div>'
  +   '<div class="cover-title">' + TOPIC.cn + '</div>'
  +   '<div class="cover-en">' + TOPIC.en + '</div>'
  +   '<div class="cover-rule"></div>'
  +   '<div class="cover-line">' + TOPIC.line + '</div>'
  + '</div>'
  + '<div class="layer cover-foot-divider"></div>'
  + '<div class="layer cover-footer"><div class="slogan">MAKE EACH ANSWER COUNT.</div>'
  +   '<div class="dots"><i class="active"></i><i></i><i></i></div></div>'
  + '</div>');

/* ---- 串讲页 ---- */
chunks.forEach(function (items, idx) {
  var head =
    '<div class="brand">'
    + '<div class="logo">' + logo('p' + idx) + '</div>'
    + '<div class="brand-title"><div class="en">C++ INTERVIEW CARD</div><div class="cn">知识点串讲 · RECAP</div></div>'
    + '<div class="brand-no"><div class="num">' + TOPIC.no + ' / 10</div><div class="tag">TOPIC RECAP</div></div>'
    + '</div><div class="divider"></div>'
    + '<div class="mod-head">'
    +   '<div class="mod-kicker"><span class="idx">MODULE ' + TOPIC.no + '</span>'
    +     '<span class="cat">' + TOPIC.en + '</span>'
    +     '<span class="range">CARD ' + TOPIC.range + '</span></div>'
    +   '<div class="cn">' + TOPIC.cn + '</div>'
    + '</div>';

  // 主线导语只在第一张串讲页出现
  var lead = idx === 0
    ? '<div class="lead"><div class="mark">&ldquo;</div>'
      + '<div class="lbl">一条主线 · MAIN THREAD</div><p>' + TOPIC.thread + '</p></div>'
    : '';

  var secLabel = chunks.length > 1
    ? '考点串讲 · KEY POINTS (' + (idx + 1) + '/' + chunks.length + ')'
    : '考点串讲 · KEY POINTS';

  var list = items.map(function (it, li) {
    return '<div class="node' + (it[3] ? ' hot' : '') + '">'
      + '<div class="dot">' + it[0] + '</div>'
      + '<div class="content">'
      +   '<div class="q">' + it[1]
      +     (it[3] ? '<span class="fire">🔥</span><span class="hot-badge">HOT</span>' : '') + '</div>'
      +   '<div class="a">' + it[2] + '</div>'
      + '</div>'
      + (li < items.length - 1 ? '<span class="gap-mark"></span>' : '')
      + '</div>';
  }).join('');

  // 金句只放在最后一张串讲页
  var quote = (idx === chunks.length - 1)
    ? '<div class="quote"><div class="ico">”</div><p>' + TOPIC.quote + '</p></div>'
    : '';

  addPage(TOPIC.slug + '-' + String(idx + 1).padStart(2, '0') + '-recap',
    '<div class="panel">'
    + '<div class="panel-bg"><div class="grid"></div><div class="dots"></div>'
    +   '<div class="arcs"></div></div>'
    + head + lead
    + '<div class="sec-lbl">' + secLabel + '</div>'
    + '<div class="tl">' + list + '<div class="tl-end"></div></div>'
    + quote
    + '<div class="foot-divider"></div>'
    + '<div class="footer"><div class="slogan">MAKE EACH ANSWER COUNT.</div>'
    +   '<div class="deco"><i class="s"></i><i class="m"></i><i class="dot"></i><i class="dot2"></i><i class="m"></i><i class="s"></i></div>'
    +   '<div class="pager"><b>' + (idx + 2) + '</b> / ' + totalPages + '</div></div>'
    + '</div>');
});

/* ---- 封面斜体数字处理 ---- */
/* ---- 缩放与导出 ---- */
var W = 720, H = 1280;
var viewports = Array.prototype.slice.call(document.querySelectorAll('.viewport'));

function fit() {
  var availW = window.innerWidth - 32;
  var availH = window.innerHeight - 96 - 48;
  var scale = Math.min(1, availW / W, availH / H);
  viewports.forEach(function (v) {
    v.querySelector('.stage').style.transform = 'scale(' + scale + ')';
    v.style.width = (W * scale) + 'px';
    v.style.height = (H * scale) + 'px';
  });
}
window.addEventListener('resize', fit);
fit();

function nextFrame() {
  return new Promise(function (r) { requestAnimationFrame(function () { requestAnimationFrame(r); }); });
}

/* 某些字体 / 布局下渐变背景会被压成 0 尺寸，html2canvas 仍拿它 createPattern；换成 1×1 透明画布 */
(function () {
  var proto = CanvasRenderingContext2D.prototype, orig = proto.createPattern;
  var blank = document.createElement('canvas');
  blank.width = blank.height = 1;
  proto.createPattern = function (img, repetition) {
    if (img && (img.width === 0 || img.height === 0)) img = blank;
    return orig.call(this, img, repetition);
  };
})();

document.getElementById('exportAll').addEventListener('click', async function () {
  if (typeof html2canvas !== 'function') {
    alert('html2canvas 尚未加载（可能网络受限）。请联网后重试，或使用系统截图。');
    return;
  }
  var btn = this, label = btn.textContent;
  btn.disabled = true;
  viewports.forEach(function (v) {
    v.querySelector('.stage').style.transform = 'none';
    v.style.width = W + 'px'; v.style.height = H + 'px';
  });
  await nextFrame();
  var failed = [];
  try {
    for (var i = 0; i < viewports.length; i++) {
      btn.textContent = '导出中 ' + (i + 1) + '/' + viewports.length + '…';
      var frame = viewports[i].querySelector('.frame');
      try {
        var canvas = await html2canvas(frame, {
        scale: 2, backgroundColor: '#e9ebf0', useCORS: true, logging: false,
        width: W, height: H, windowWidth: W, windowHeight: H,
        onclone: function (doc) {
          // html2canvas 不支持 border-image 和 background-clip:text（渐变字会变成色块），导出时改用纯色
          var css = doc.createElement('style');
          css.textContent = '.mod-line .meta{border-image:none!important;'
            + 'border-left:3px solid var(--theme,#4c8ff0)!important;}'
            + '.mod-line .n{background:none!important;color:var(--theme,#3949ab)!important;}';
          doc.head.appendChild(css);
        }
      });
      var a = document.createElement('a');
      a.download = frame.dataset.name + '.png';
      a.href = canvas.toDataURL('image/png');
      a.click();
      } catch (err) {
        failed.push(frame.dataset.name + '（' + err.message + '）');
      }
      await new Promise(function (r) { setTimeout(r, 300); });
    }
    if (failed.length) {
      alert('有 ' + failed.length + ' 页导出失败，其余已完成：\n' + failed.join('\n'));
    }
  } catch (e) {
    alert('导出失败：' + e.message);
  } finally {
    btn.disabled = false; btn.textContent = label; fit();
  }
});
</script>
</body>
</html>
"""

INDEX_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>C++ 面试口袋卡片 · 主题总结目录</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
    background: #e9ebf0; color: #1f232c; padding: 48px 20px 64px;
  }
  .wrap { max-width: 980px; margin: 0 auto; }
  .head {
    background: linear-gradient(165deg, #ffffff 0%, #f4f7ff 45%, #e8eefc 100%);
    border: 1px solid #dfe5f4;
    border-radius: 20px; padding: 40px 42px; margin-bottom: 26px;
    box-shadow: 0 14px 34px rgba(40,55,100,.08);
  }
  .head .k { font-size: 12px; letter-spacing: 4px; color: #0b7c8c; font-weight: 700; }
  .head h1 { margin-top: 14px; font-size: 38px; letter-spacing: 1px; }
  .head p { margin-top: 14px; font-size: 15px; line-height: 1.8; color: #4a4f5a; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
  a.card {
    display: block; text-decoration: none; color: inherit;
    background: #fff; border: 1px solid #e2e5ec; border-radius: 16px;
    padding: 22px 24px; position: relative; overflow: hidden;
    transition: transform .15s ease, box-shadow .15s ease;
  }
  a.card::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px;
    background: linear-gradient(180deg, #4c6ef5, #3b5bdb 55%, #12b5c9);
  }
  a.card:hover { transform: translateY(-3px); box-shadow: 0 14px 32px rgba(40,55,100,.14); }
  .card .no { font-size: 12px; letter-spacing: 2px; color: #9aa0ac; font-weight: 700; }
  .card h2 { margin-top: 8px; font-size: 22px; letter-spacing: .5px; }
  .card .en { margin-top: 6px; font-size: 11px; letter-spacing: 2px; color: #c4c9d4; }
  .card .line { margin-top: 12px; font-size: 13.5px; line-height: 1.65; color: #4a4f5a; }
  .card .foot { margin-top: 14px; display: flex; gap: 8px; }
  .tag {
    font-size: 11px; letter-spacing: 1px; padding: 5px 10px; border-radius: 999px;
    background: #eef1fa; color: #3949ab; font-weight: 700;
  }
  .tag.gold { background: #e7fbfd; color: #0b7c8c; }
</style>
</head>
<body>
  <div class="wrap">
    <div class="head">
      <div class="k">SERIES COMPLETE · 全系列收官</div>
      <h1>C++ 面试口袋卡片 · 主题总结</h1>
      <p>86 题 · 10 个主题。每个主题一份 HTML，内含 1 张封面页 + 若干张知识点串讲页（题目 + 一句话回答 + 卡片序号），可一键批量导出 9:16 高清图。</p>
    </div>
    <div class="grid">
__CARDS__
    </div>
  </div>
</body>
</html>
"""


def build():
    for t in TOPICS:
        payload = {
            "slug": t["slug"], "no": t["no"], "cn": t["cn"], "en": t["en"],
            "range": t["range"], "line": t["line"], "thread": t["thread"],
            "quote": t["quote"], "items": t["items"],
        }
        html = (TEMPLATE
                .replace("__TOPIC_JSON__", json.dumps(payload, ensure_ascii=False))
                .replace("__PER_PAGE__", str(PER_PAGE))
                .replace("__FIRST_PAGE_MAX__", "0")
                .replace("__NO__", t["no"])
                .replace("__CN__", t["cn"]))
        path = os.path.join(HERE, t["slug"] + ".html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        pages = 1 + (len(t["items"]) + PER_PAGE - 1) // PER_PAGE
        print("生成 %-24s  %2d 题 → %d 页" % (t["slug"] + ".html", len(t["items"]), pages))

    cards = []
    for t in TOPICS:
        hot = sum(1 for it in t["items"] if it[3])
        pages = 1 + (len(t["items"]) + PER_PAGE - 1) // PER_PAGE
        cards.append(
            '      <a class="card" href="%s.html">\n'
            '        <div class="no">MODULE %s · %s</div>\n'
            '        <h2>%s</h2>\n'
            '        <div class="en">%s</div>\n'
            '        <div class="line">%s</div>\n'
            '        <div class="foot"><span class="tag">%d 题 / %d 页</span>'
            '<span class="tag gold">%d 个高频</span></div>\n'
            '      </a>' % (t["slug"], t["no"], t["range"], t["cn"], t["en"], t["line"],
                            len(t["items"]), pages, hot)
        )
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX_TEMPLATE.replace("__CARDS__", "\n".join(cards)))
    print("生成 index.html")


if __name__ == "__main__":
    build()
