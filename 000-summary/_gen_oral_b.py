#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""口述稿卡片生成器。内容来自 summary-plan-b-oral.md，版式独立于串讲卡。

用法:
    python3 _gen_oral_b.py

产出:
    b-oral-00-open.html、b-oral-01.html … b-oral-15.html、b-oral-16-close.html
    index-oral.html
"""

import html
import os
import re

from _gen_summary_b import ARC_GRADIENT, PART_THEME

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "summary-plan-b-oral.md")

PART_BY_PREFIX = (
    ("篇一", "篇一 · 一个对象的一生"),
    ("篇二", "篇二 · 一行代码到一条指令"),
    ("篇三", "篇三 · 一次请求的旅程"),
    ("终章", "终章 · 架构的落地"),
)


def part_key(heading):
    for prefix, key in PART_BY_PREFIX:
        if heading.startswith(prefix):
            return key
    return "篇一 · 一个对象的一生"


def fmt(text):
    text = html.escape(text.strip())
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", text)


def parse_beat(paragraph):
    ids = re.findall(r"【(\d{3})】", paragraph)
    text = re.sub(r"【\d{3}】", "", paragraph)
    text = re.sub(r"\s+", " ", text).strip()
    return {"ids": ids, "text": text}


def parse(path):
    part = "开场"
    sections = []
    current = None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if line.startswith("# ") and not line.startswith("## "):
            part = line[2:].strip()
            continue
        if line.startswith("## "):
            if current:
                sections.append(current)
            title = line[3:].strip()
            kind = "act"
            no = ""
            if title.startswith("总开场"):
                kind, no = "open", "00"
            elif title.startswith("总收尾"):
                kind, no = "close", "16"
            else:
                m = re.match(r"幕\s*(\d+)\s*·\s*(.+)", title)
                no = "%02d" % int(m.group(1))
                title = m.group(2)
            current = {
                "kind": kind, "no": no, "title": title, "part": part,
                "bridge_in": "", "bridge_out": "", "beats": [], "order": [],
            }
            continue
        if current is None or not line.strip() or line.strip() == "---":
            continue
        if line.startswith("> 顺序"):
            current["order"] = re.findall(r"\d{3}", line)
        elif line.startswith("**承上**"):
            current["bridge_in"] = line.split("：", 1)[1].strip()
        elif line.startswith("**启下**"):
            current["bridge_out"] = line.split("：", 1)[1].strip()
        else:
            current["beats"].append(parse_beat(line))
    if current:
        sections.append(current)
    return sections


def weight(text):
    return len(re.sub(r"\s+", "", text))


def chunk_beats(section):
    beats = section["beats"]
    pages = []
    buf, used = [], 0
    first = True
    for i, beat in enumerate(beats):
        remain = len(beats) - i - 1
        limit = 280 if first and section["bridge_in"] else 360
        if remain == 0 and section["bridge_out"]:
            limit -= 90
        w = weight(beat["text"])
        if buf and used + w > limit:
            pages.append(buf)
            buf, used, first = [], 0, False
        buf.append(beat)
        used += w
    if buf:
        pages.append(buf)
    return pages or [[]]


def beat_html(beat):
    chips = "".join('<span class="chip">%s</span>' % i for i in beat["ids"])
    side = '<div class="side">%s</div>' % (chips or '<span class="chip ghost">·</span>')
    return '<article class="beat">%s<p>%s</p></article>' % (side, fmt(beat["text"]))


def bridge_html(kind, text):
    label = "承上" if kind == "in" else "启下"
    en = "FROM LAST ACT" if kind == "in" else "INTO NEXT ACT"
    return (
        '<section class="bridge %s"><div class="tag"><b>%s</b><span>%s</span></div><p>%s</p></section>'
        % (kind, label, en, fmt(text))
    )


def cover_html(section, pages):
    theme_label = "OPENING" if section["kind"] == "open" else (
        "CLOSING" if section["kind"] == "close" else PART_THEME[part_key(section["part"])]["label"]
    )
    hook = section["bridge_in"] or (section["beats"][0]["text"] if section["beats"] else "")
    count = sum(len(b["ids"]) for b in section["beats"])
    meta = "%d 段口述" % len(section["beats"])
    if count:
        meta += " · %d 张原卡" % count
    meta += " · 共 %d 页" % (pages + 1)
    order = ""
    if section["order"]:
        order = '<div class="order">%s</div>' % '<i>→</i>'.join(
            '<span>%s</span>' % i for i in section["order"])
    return (
        '<div class="panel cover">'
        '<div class="wm">%s</div>'
        '<div class="top"><div><div class="brand">C++ ORAL SCRIPT</div>'
        '<div class="sub">口述稿 · 可以直接照着讲</div></div>'
        '<div class="no">%s</div></div>'
        '<div class="kicker">%s</div>'
        '<div class="hero"><div class="big">%s</div><div class="act">%s</div></div>'
        '<h1>%s</h1>'
        '<div class="rule"></div>'
        '<p class="hook">%s</p>'
        '%s'
        '<div class="foot"><span>%s</span><span>%s</span></div>'
        '</div>'
    ) % (
        section["no"], theme_label, section["no"], section["no"],
        "OPENING" if section["kind"] == "open" else (
            "CLOSING" if section["kind"] == "close" else "ACT " + section["no"]
        ),
        html.escape(section["title"]), fmt(hook), order, meta,
        html.escape(section["part"]),
    )


def script_html(section, beats, idx, total):
    parts = [
        '<div class="panel script">',
        '<div class="top"><div><div class="brand">ORAL SCRIPT</div>',
        '<div class="sub">%s</div></div>' % html.escape(section["part"]),
        '<div class="no">%s <small>/ %d</small></div></div>' % (idx + 1, total),
        '<h1>%s</h1>' % html.escape(section["title"]),
    ]
    if idx == 0 and section["bridge_in"]:
        parts.append(bridge_html("in", section["bridge_in"]))
    parts.append('<div class="beats">')
    parts.extend(beat_html(b) for b in beats)
    parts.append('</div>')
    if idx == total - 1 and section["bridge_out"]:
        parts.append(bridge_html("out", section["bridge_out"]))
    parts.append('<div class="foot"><span>卡号不用念出来</span><b>%d / %d</b></div>' % (idx + 2, total + 1))
    parts.append('</div>')
    return "".join(parts)


PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>__TITLE__</title>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<style>
  :root {
    --theme: __ACCENT__; --theme-2: __ACCENT2__; --theme-soft: __SOFT__;
    --theme-deep: __DEEP__; --theme-rgb: __RGB__; --theme2-rgb: __RGB2__;
    --ink: #243041; --muted: #667385;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
    background: #f3f5f9; color: var(--ink);
    display: flex; flex-direction: column; align-items: center;
    padding: 96px 16px 48px;
  }
  .toolbar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 50;
    display: flex; align-items: center; justify-content: center; gap: 14px;
    padding: 12px 16px; background: rgba(255,255,255,.96);
    border-bottom: 1px solid #e4e8ef;
  }
  .btn {
    border: none; cursor: pointer; background: var(--theme); color: #fff;
    font-size: 14px; font-weight: 700; padding: 10px 16px; border-radius: 8px;
  }
  .toolbar span, .toolbar a { color: var(--muted); font-size: 12px; text-decoration: none; }
  .pages { display: flex; flex-direction: column; align-items: center; gap: 28px; }
  .viewport { overflow: hidden; }
  .stage { transform-origin: top left; }
  .frame { width: 720px; height: 1280px; background: #f0f3f8; padding: 18px; }
  .panel {
    position: relative; width: 100%; height: 100%; overflow: hidden;
    background: #fff; border: 1px solid #e2e8f4; border-radius: 16px;
    box-shadow: 0 16px 40px rgba(74,127,232,.07);
    display: flex; flex-direction: column;
  }
  .panel::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 7px;
    background: linear-gradient(180deg, var(--theme), var(--theme-2));
  }
  .cover { padding: 52px 52px 40px 60px; color: var(--ink); }
  .cover .wm {
    position: absolute; right: -20px; bottom: 40px;
    font-size: 280px; line-height: .8; font-weight: 900; letter-spacing: -.06em;
    color: transparent; -webkit-text-stroke: 2px rgba(var(--theme-rgb), .08);
  }
  .top, .hero, .kicker, h1, .rule, .hook, .foot, .beats, .bridge { position: relative; }
  .top { display: flex; justify-content: space-between; align-items: flex-start; }
  .brand { font-size: 18px; font-weight: 800; letter-spacing: 1px; }
  .sub { margin-top: 6px; color: var(--muted); font-size: 13px; letter-spacing: 1px; }
  .no { color: var(--theme); font-size: 28px; font-weight: 900; }
  .kicker {
    align-self: flex-start; margin-top: 54px;
    color: var(--theme-deep); background: var(--theme-soft);
    border-radius: 6px; padding: 8px 12px;
    font-size: 12px; font-weight: 800; letter-spacing: 2px;
  }
  .hero { display: flex; align-items: flex-end; gap: 16px; margin-top: 28px; }
  .big {
    font-size: 118px; line-height: .82; font-weight: 900; letter-spacing: -.04em;
    background: linear-gradient(135deg, var(--theme), var(--theme-2));
    -webkit-background-clip: text; background-clip: text; color: transparent;
  }
  .act { padding-bottom: 12px; border-left: 3px solid var(--theme-2); padding-left: 14px; font-size: 20px; font-weight: 800; }
  .cover h1 { margin-top: 34px; max-width: 560px; font-size: 58px; line-height: 1.18; }
  .rule { width: 116px; height: 4px; margin: 24px 0; border-radius: 2px; background: linear-gradient(90deg, var(--theme), var(--theme-2)); }
  .hook { max-width: 540px; color: #4f5d6f; font-size: 22px; line-height: 1.75; }
  .order {
    position: relative; margin-top: 26px; max-width: 580px;
    display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
  }
  .order span {
    padding: 5px 10px; border-radius: 7px; background: var(--theme-soft);
    color: var(--theme-deep); font-size: 15px; font-weight: 800;
  }
  .order i { color: var(--muted); font-style: normal; font-size: 14px; }
  .foot {
    margin-top: auto; padding-top: 22px; border-top: 1px solid #e8ecf2;
    display: flex; justify-content: space-between; color: var(--muted); font-size: 13px;
  }
  .script { padding: 34px 36px 28px 46px; }
  .script .no { font-size: 22px; }
  .script .no small { color: var(--muted); font-size: 14px; font-weight: 700; }
  .script h1 { margin: 22px 0 18px; font-size: 32px; line-height: 1.25; }
  .bridge { margin-bottom: 16px; padding: 14px 16px; border-radius: 12px; background: var(--theme-soft); }
  .bridge.out { margin-top: 16px; margin-bottom: 0; background: #fff8ee; }
  .bridge .tag { display: flex; align-items: baseline; gap: 8px; margin-bottom: 6px; }
  .bridge b { color: var(--theme-deep); font-size: 13px; letter-spacing: 1px; }
  .bridge.out b { color: #9a6230; }
  .bridge .tag span { color: var(--muted); font-size: 11px; letter-spacing: 1px; }
  .bridge p { color: #3e4b5e; font-size: 17px; line-height: 1.7; }
  .beats { display: flex; flex-direction: column; gap: 16px; }
  .beat {
    display: grid; grid-template-columns: 58px 1fr; gap: 14px;
    padding: 16px 16px 16px 12px; border: 1px solid #e7edf5; border-radius: 12px;
    background: #f9fbfe;
  }
  .side { display: flex; flex-direction: column; gap: 6px; }
  .chip {
    display: inline-flex; align-items: center; justify-content: center;
    min-height: 28px; border-radius: 7px; background: var(--theme); color: #fff;
    font-size: 13px; font-weight: 800;
  }
  .chip.ghost { background: #e7edf5; color: #9aa6b5; }
  .beat p { color: #2d3948; font-size: 18px; line-height: 1.75; }
  code {
    font-family: "SFMono-Regular", Consolas, Menlo, monospace;
    font-size: .92em; color: var(--theme-deep); background: var(--theme-soft);
    padding: 0 5px; border-radius: 4px;
  }
  .script .foot b { color: var(--theme); font-size: 16px; }
</style>
</head>
<body>
  <div class="toolbar" data-html2canvas-ignore="true">
    <button id="exportAll" class="btn">导出本幕口述稿 (PNG)</button>
    <span>__HINT__ · 720 × 1280</span>
    <a href="index-oral.html">← 返回口述稿目录</a>
  </div>
  <div class="pages" id="pages">__PAGES__</div>
<script>
var W = 720, H = 1280;
var viewports = Array.prototype.slice.call(document.querySelectorAll('.viewport'));
function fit() {
  var scale = Math.min(1, (window.innerWidth - 32) / W, (window.innerHeight - 144) / H);
  viewports.forEach(function (v) {
    v.querySelector('.stage').style.transform = 'scale(' + scale + ')';
    v.style.width = (W * scale) + 'px';
    v.style.height = (H * scale) + 'px';
  });
}
window.addEventListener('resize', fit); fit();
function nextFrame() { return new Promise(function (r) { requestAnimationFrame(function () { requestAnimationFrame(r); }); }); }
document.getElementById('exportAll').addEventListener('click', async function () {
  if (typeof html2canvas !== 'function') { alert('html2canvas 尚未加载。'); return; }
  var btn = this, label = btn.textContent; btn.disabled = true;
  viewports.forEach(function (v) { v.querySelector('.stage').style.transform = 'none'; v.style.width = W + 'px'; v.style.height = H + 'px'; });
  await nextFrame();
  try {
    for (var i = 0; i < viewports.length; i++) {
      btn.textContent = '导出中 ' + (i + 1) + '/' + viewports.length + '…';
      var frame = viewports[i].querySelector('.frame');
      var canvas = await html2canvas(frame, { scale: 2, backgroundColor: '#f0f3f8', useCORS: true, logging: false, width: W, height: H, windowWidth: W, windowHeight: H });
      var a = document.createElement('a'); a.download = frame.dataset.name + '.png'; a.href = canvas.toDataURL('image/png'); a.click();
      await new Promise(function (r) { setTimeout(r, 300); });
    }
  } catch (e) { alert('导出失败：' + e.message); }
  finally { btn.disabled = false; btn.textContent = label; fit(); }
});
</script>
</body>
</html>
"""


def slug_for(section):
    if section["kind"] == "open":
        return "b-oral-00-open"
    if section["kind"] == "close":
        return "b-oral-16-close"
    return "b-oral-" + section["no"]


def render(section):
    theme = PART_THEME[part_key(section["part"])]
    groups = chunk_beats(section)
    frames = [cover_html(section, len(groups))]
    frames.extend(script_html(section, beats, i, len(groups)) for i, beats in enumerate(groups))
    pages = []
    for i, frame in enumerate(frames):
        name = "%s-%02d" % (slug_for(section), i)
        pages.append(
            '<div class="viewport"><div class="stage"><div class="frame" data-name="%s">%s</div></div></div>'
            % (name, frame)
        )
    title = "口述稿 · %s %s" % (section["no"], section["title"])
    hint = "总开场" if section["kind"] == "open" else (
        "总收尾" if section["kind"] == "close" else "第 %s 幕" % section["no"]
    )
    return PAGE.replace("__TITLE__", html.escape(title)).replace("__HINT__", hint).replace(
        "__ACCENT__", theme["accent"]).replace("__ACCENT2__", theme["accent2"]).replace(
        "__SOFT__", theme["soft"]).replace("__DEEP__", theme["deep"]).replace(
        "__RGB__", theme["rgb"]).replace("__RGB2__", theme["rgb2"]).replace(
        "__PAGES__", "\n".join(pages)), len(frames)


INDEX = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>C++ 面试口述稿卡片</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: "PingFang SC", "Microsoft YaHei", sans-serif; background: #f3f5f9; color: #243041; padding: 42px 20px 70px; }
  .wrap { max-width: 1120px; margin: 0 auto; }
  .head { position: relative; overflow: hidden; background: linear-gradient(165deg, #fff, #f8fbff 50%, #eef4ff); border: 1px solid #e2e8f4; border-radius: 16px; padding: 42px 46px 38px; box-shadow: 0 16px 40px rgba(74,127,232,.08); }
  .head::after { content: ""; position: absolute; left: 46px; right: 46px; bottom: 0; height: 4px; background: __ARC__; }
  .k { color: #2eb8a8; font-size: 12px; font-weight: 800; letter-spacing: 3px; }
  h1 { margin-top: 14px; font-size: 38px; }
  p { max-width: 860px; margin-top: 14px; color: #5a6573; font-size: 15px; line-height: 1.85; }
  .switch { display: flex; gap: 10px; margin-top: 18px; }
  .switch a { color: #4a7fe8; text-decoration: none; font-weight: 700; font-size: 13px; border: 1px solid #d6e2f7; background: #fff; border-radius: 8px; padding: 9px 14px; }
  .part { margin-top: 32px; }
  .part h2 { font-size: 22px; }
  .part .en { margin-left: 12px; color: var(--theme); font-size: 11px; letter-spacing: 2px; }
  .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-top: 14px; }
  a.card { display: grid; grid-template-columns: 72px 1fr; gap: 16px; position: relative; overflow: hidden; text-decoration: none; color: inherit; background: #fff; border: 1px solid #e4e8ef; border-radius: 12px; padding: 20px 20px 18px 16px; }
  a.card::before { content: attr(data-no); display: flex; justify-content: center; color: var(--theme); font-size: 32px; font-weight: 900; border-right: 1px solid #e8ecf2; }
  a.card::after { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 4px; background: linear-gradient(90deg, var(--theme), var(--theme2)); }
  .card h3 { font-size: 20px; line-height: 1.35; }
  .card .en2 { margin-top: 7px; color: var(--theme); font-size: 11px; font-weight: 800; letter-spacing: 1px; }
  .card .line { margin-top: 8px; color: #556170; font-size: 14px; line-height: 1.6; }
  .tag { display: inline-block; margin-top: 12px; margin-right: 6px; background: var(--soft); color: var(--deep); border-radius: 4px; padding: 4px 8px; font-size: 11px; font-weight: 800; }
  @media (max-width: 760px) { .grid { grid-template-columns: 1fr; } .head, body { padding-left: 16px; padding-right: 16px; } }
</style>
</head>
<body><div class="wrap">
  <div class="head">
    <div class="k">ORAL SCRIPT · 口述稿卡片</div>
    <h1>把每一幕讲出来</h1>
    <p>这是和串讲卡分开的一套卡片。串讲卡负责题目和一句话答案；口述稿卡片按「承上 → 口述 → 启下」分页，字号按朗读距离排，原卡号只标在旁边，讲的时候不用念。</p>
    <div class="switch"><a href="index-b.html">← 返回方案B串讲</a></div>
  </div>
  __PARTS__
</div></body></html>
"""


def build():
    sections = parse(SRC)
    assert len(sections) == 17, "应有开场、15 幕、收尾，实际 %d" % len(sections)
    rendered = []
    for section in sections:
        html_text, pages = render(section)
        slug = slug_for(section)
        with open(os.path.join(HERE, slug + ".html"), "w", encoding="utf-8") as f:
            f.write(html_text)
        rendered.append((section, slug, pages))
        print("生成 %-22s %2d 页" % (slug + ".html", pages))

    groups = []
    for section, slug, pages in rendered:
        key = part_key(section["part"])
        if not groups or groups[-1][0] != key:
            groups.append((key, []))
        groups[-1][1].append((section, slug, pages))
    parts = []
    for key, items in groups:
        theme = PART_THEME[key]
        cards = []
        for section, slug, pages in items:
            cards.append(
                '<a class="card" data-no="%s" href="%s.html"><div><h3>%s</h3>'
                '<div class="en2">%s</div><div class="line">%s</div><span class="tag">%d 页</span></div></a>'
                % (section["no"], slug, html.escape(section["title"]), theme["label"],
                   html.escape(section["bridge_in"] or section["beats"][0]["text"][:42]), pages)
            )
        parts.append(
            '<section class="part" style="--theme:%s;--theme2:%s;--soft:%s;--deep:%s">'
            '<h2>%s<span class="en">%s</span></h2><div class="grid">%s</div></section>'
            % (theme["accent"], theme["accent2"], theme["soft"], theme["deep"],
               html.escape(key), theme["label"], "".join(cards))
        )
    with open(os.path.join(HERE, "index-oral.html"), "w", encoding="utf-8") as f:
        f.write(INDEX.replace("__ARC__", ARC_GRADIENT).replace("__PARTS__", "\n".join(parts)))
    print("生成 index-oral.html")


if __name__ == "__main__":
    build()
