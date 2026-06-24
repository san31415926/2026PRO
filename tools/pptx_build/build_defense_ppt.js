const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
const root = path.resolve(__dirname, "..", "..");
const outFile = path.join(root, "张捷_答辩PPT_终稿_占位版.pptx");

const figures = {
  architecture: path.join(root, "fig3_1_architecture.svg"),
  functionStructure: path.join(root, "fig3_2_function_structure.svg"),
  er: path.join(root, "fig3_3_er.svg"),
  checkoutFlow: path.join(root, "fig4_8_checkout_flow.svg"),
  groupFlow: path.join(root, "fig4_12_group_flow.svg"),
  seckillFlow: path.join(root, "fig4_14_seckill_flow.svg"),
};

const colors = {
  coverBlue: "2472C8",
  coverPurple: "4458D8",
  coverLight: "EAF7FB",
  bg: "F7F9FC",
  white: "FFFFFF",
  navy: "1B2E4B",
  blue: "2176C7",
  teal: "1D9B88",
  gold: "D9A64D",
  coral: "E57958",
  text: "22313F",
  muted: "617487",
  line: "D6E0EA",
  softBlue: "ECF5FC",
  softTeal: "EDF9F5",
  softGold: "FFF7EA",
  softCoral: "FFF0EB",
  dark: "102131",
};

const fonts = {
  title: "Microsoft YaHei",
  body: "Microsoft YaHei",
  light: "Microsoft YaHei Light",
};

pptx.layout = "LAYOUT_16x9";
pptx.author = "OpenAI Codex";
pptx.company = "SmartMall_BiShe";
pptx.subject = "毕业设计答辩PPT";
pptx.title = "基于 Python 和 Vue 的数码电子商城的设计与实现";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: fonts.title,
  bodyFontFace: fonts.body,
  lang: "zh-CN",
};

function addText(slide, text, opts = {}) {
  slide.addText(text, {
    fontFace: fonts.body,
    fontSize: 16,
    color: colors.text,
    margin: 0,
    valign: "top",
    breakLine: false,
    ...opts,
  });
}

function addFooter(slide, text) {
  addText(slide, text, {
    x: 0.72,
    y: 5.16,
    w: 8.2,
    h: 0.12,
    fontSize: 9.5,
    color: colors.muted,
  });
}

function addCard(slide, x, y, w, h, options = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.05,
    line: { color: options.lineColor || colors.line, width: options.lineWidth || 1 },
    fill: { color: options.fillColor || colors.white },
    shadow: options.shadow
      ? { type: "outer", color: "000000", blur: 2, offset: 1, angle: 45, opacity: 0.12 }
      : undefined,
  });
  if (options.barColor) {
    slide.addShape(pptx.ShapeType.rect, {
      x,
      y,
      w: 0.12,
      h,
      line: { color: options.barColor, width: 0 },
      fill: { color: options.barColor },
    });
  }
}

function addTag(slide, x, y, w, label, fill, color = colors.navy) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h: 0.3,
    rectRadius: 0.05,
    line: { color: fill, width: 0 },
    fill: { color: fill },
  });
  addText(slide, label, {
    x,
    y: y + 0.065,
    w,
    h: 0.14,
    fontSize: 10.5,
    bold: true,
    color,
    align: "center",
  });
}

function addCardTitle(slide, x, y, w, title, color = colors.navy) {
  addText(slide, title, {
    x,
    y,
    w,
    h: 0.2,
    fontFace: fonts.title,
    fontSize: 17,
    bold: true,
    color,
  });
}

function addBulletList(slide, items, x, y, w, h, fontSize = 13, color = colors.text) {
  const runs = [];
  items.forEach((item, idx) => {
    runs.push({
      text: item,
      options: { bullet: true, breakLine: idx !== items.length - 1 },
    });
  });
  slide.addText(runs, {
    x,
    y,
    w,
    h,
    margin: 0.02,
    fontFace: fonts.body,
    fontSize,
    color,
    paraSpaceAfterPt: 9,
    valign: "top",
  });
}

function addMetric(slide, x, y, w, h, value, label, fill, accent) {
  addCard(slide, x, y, w, h, { fillColor: fill, lineColor: fill });
  addText(slide, value, {
    x: x + 0.1,
    y: y + 0.12,
    w: w - 0.2,
    h: 0.2,
    fontSize: 22,
    bold: true,
    color: accent,
    align: "center",
  });
  addText(slide, label, {
    x: x + 0.1,
    y: y + 0.52,
    w: w - 0.2,
    h: 0.12,
    fontSize: 10,
    color: colors.muted,
    align: "center",
  });
}

function addPageChrome(slide, title, index, accent = colors.blue, soft = colors.softBlue) {
  slide.background = { color: colors.bg };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 10,
    h: 0.92,
    line: { color: soft, width: 0 },
    fill: { color: soft },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.58,
    y: 0.27,
    w: 0.16,
    h: 0.36,
    line: { color: accent, width: 0 },
    fill: { color: accent },
  });
  addText(slide, title, {
    x: 0.84,
    y: 0.2,
    w: 5.9,
    h: 0.36,
    fontFace: fonts.title,
    fontSize: 28,
    bold: true,
    color: colors.navy,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 8.82,
    y: 0.19,
    w: 0.62,
    h: 0.38,
    rectRadius: 0.05,
    line: { color: accent, width: 0 },
    fill: { color: accent },
  });
  addText(slide, String(index).padStart(2, "0"), {
    x: 8.93,
    y: 0.285,
    w: 0.4,
    h: 0.12,
    fontSize: 10,
    color: colors.white,
    bold: true,
    align: "center",
  });
}

function addFigure(slide, filePath, x, y, w, h, placeholderTitle, placeholderNote) {
  if (fs.existsSync(filePath)) {
    slide.addImage({
      path: filePath,
      x,
      y,
      w,
      h,
      sizing: { type: "contain", w, h },
    });
    return;
  }
  addCard(slide, x, y, w, h, { fillColor: colors.white, lineColor: colors.line });
  addText(slide, placeholderTitle, {
    x: x + 0.2,
    y: y + 0.3,
    w: w - 0.4,
    h: 0.2,
    fontSize: 16,
    bold: true,
    color: colors.muted,
    align: "center",
  });
  addText(slide, placeholderNote, {
    x: x + 0.3,
    y: y + 0.8,
    w: w - 0.6,
    h: 0.4,
    fontSize: 11,
    color: colors.muted,
    align: "center",
  });
}

function addScreenshotSlot(slide, x, y, w, h, title, hint, accent = colors.blue) {
  addCard(slide, x, y, w, h, { fillColor: colors.white, lineColor: colors.line, shadow: true });
  slide.addShape(pptx.ShapeType.rect, {
    x,
    y,
    w,
    h: 0.26,
    line: { color: accent, width: 0 },
    fill: { color: accent },
  });
  addText(slide, title, {
    x: x + 0.14,
    y: y + 0.065,
    w: w - 0.28,
    h: 0.1,
    fontSize: 10.5,
    bold: true,
    color: colors.white,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: x + 0.22,
    y: y + 0.42,
    w: w - 0.44,
    h: h - 0.98,
    rectRadius: 0.04,
    line: { color: colors.line, width: 1, dash: "dash" },
    fill: { color: "FBFCFE" },
  });
  addText(slide, "这里预留给你的系统运行截图", {
    x: x + 0.36,
    y: y + 0.98,
    w: w - 0.72,
    h: 0.18,
    fontSize: 13,
    bold: true,
    color: colors.muted,
    align: "center",
  });
  addText(slide, hint, {
    x: x + 0.34,
    y: y + 1.28,
    w: w - 0.68,
    h: 0.48,
    fontSize: 10.5,
    color: colors.muted,
    align: "center",
    valign: "mid",
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: x + 0.22,
    y: y + h - 0.34,
    w: w - 0.44,
    h: 0.16,
    rectRadius: 0.02,
    line: { color: colors.line, width: 1, dash: "dash" },
    fill: { color: colors.white },
  });
}

function addCoverDecoration(slide) {
  slide.background = { color: colors.coverBlue };
  slide.addShape(pptx.ShapeType.rect, {
    x: 5.1,
    y: 0,
    w: 4.9,
    h: 5.625,
    line: { color: colors.coverPurple, width: 0 },
    fill: { color: colors.coverPurple },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: -1.2,
    y: -0.9,
    w: 4.6,
    h: 3.1,
    line: { color: colors.white, width: 0 },
    fill: { color: colors.white, transparency: 16 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: -0.9,
    y: -0.55,
    w: 3.4,
    h: 2.4,
    line: { color: colors.coverLight, width: 0 },
    fill: { color: colors.coverLight, transparency: 26 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 7.45,
    y: 4.2,
    w: 3.7,
    h: 2.1,
    line: { color: colors.white, width: 0 },
    fill: { color: colors.white, transparency: 18 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 8.05,
    y: 4.55,
    w: 3.0,
    h: 1.55,
    line: { color: colors.coverLight, width: 0 },
    fill: { color: colors.coverLight, transparency: 12 },
  });
}

function addScreenshotPairPage(title, index, leftTitle, leftHint, rightTitle, rightHint, accent) {
  const slide = pptx.addSlide();
  addPageChrome(slide, title, index, accent, colors.softBlue);
  addText(slide, "这一页只做系统运行展示，后续你直接把自己的截图替换到占位框里即可。", {
    x: 0.72,
    y: 1.03,
    w: 8.4,
    h: 0.18,
    fontSize: 12.5,
    color: colors.muted,
  });
  addScreenshotSlot(slide, 0.72, 1.42, 4.05, 3.55, leftTitle, leftHint, accent);
  addScreenshotSlot(slide, 5.22, 1.42, 4.05, 3.55, rightTitle, rightHint, accent);
  addFooter(slide, "替换建议：优先使用有数据、有状态变化、能一眼看出功能的截图");
}

// Slide 1 Cover
{
  const slide = pptx.addSlide();
  addCoverDecoration(slide);
  addText(slide, "基于 Python 和 Vue 的\n数码电子商城的设计与实现", {
    x: 2.5,
    y: 1.03,
    w: 6.25,
    h: 1.45,
    fontFace: fonts.title,
    fontSize: 33,
    bold: true,
    color: colors.white,
    fit: "shrink",
  });
  addText(slide, "答辩PPT", {
    x: 2.53,
    y: 2.85,
    w: 2.3,
    h: 0.35,
    fontFace: fonts.title,
    fontSize: 28,
    bold: true,
    color: colors.white,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 2.42,
    y: 3.65,
    w: 7.0,
    h: 1.28,
    rectRadius: 0.05,
    line: { color: "6BB6E4", width: 0 },
    fill: { color: "2E84C9", transparency: 8 },
  });
  addBulletList(slide, [
    "答辩同学：张捷  软件工程 2022-3班",
    "指导老师：侯爱民",
    "课题方向：数码电子商城系统设计与实现",
  ], 2.72, 3.95, 5.9, 0.78, 14.5, colors.white);
}

// Slide 2 Main content
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "课题主要内容", 1, colors.blue, colors.softBlue);
  addText(slide, "本课题围绕“做一个能完整运行的数码电子商城系统”展开，不只是展示页面，还要把业务流程和活动规则做通。", {
    x: 0.72,
    y: 1.0,
    w: 8.5,
    h: 0.22,
    fontSize: 13,
    color: colors.muted,
  });
  addCard(slide, 0.72, 1.44, 2.72, 3.2, { fillColor: colors.white, lineColor: colors.line, barColor: colors.blue, shadow: true });
  addCard(slide, 3.64, 1.44, 2.72, 3.2, { fillColor: colors.white, lineColor: colors.line, barColor: colors.teal, shadow: true });
  addCard(slide, 6.56, 1.44, 2.72, 3.2, { fillColor: colors.white, lineColor: colors.line, barColor: colors.gold, shadow: true });
  addTag(slide, 0.94, 1.66, 1.05, "内容一", colors.softBlue, colors.blue);
  addTag(slide, 3.86, 1.66, 1.05, "内容二", colors.softTeal, colors.teal);
  addTag(slide, 6.78, 1.66, 1.05, "内容三", colors.softGold, colors.gold);
  addCardTitle(slide, 0.94, 2.08, 2.0, "用户端商城功能");
  addCardTitle(slide, 3.86, 2.08, 2.0, "营销活动功能");
  addCardTitle(slide, 6.78, 2.08, 2.0, "后台管理功能");
  addBulletList(slide, [
    "完成商品浏览、商品详情、购物车、结算、订单等基础交易流程。",
    "让用户可以从看商品一直走到生成订单。",
  ], 0.96, 2.52, 2.05, 1.6, 13);
  addBulletList(slide, [
    "实现优惠券、积分、拼团、秒杀等活动能力。",
    "让系统不只是普通下单，还能体现规则差异。",
  ], 3.88, 2.52, 2.05, 1.6, 13);
  addBulletList(slide, [
    "实现商品、订单、会员、活动配置和数据看板管理。",
    "体现前台展示和后台配置之间的联动关系。",
  ], 6.8, 2.52, 2.05, 1.6, 13);
  addFooter(slide, "这一页主要告诉老师：你的课题不是单页展示，而是一套完整系统");
}

// Slide 3 Goal and significance
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "课题目标和意义", 2, colors.teal, colors.softTeal);
  addCard(slide, 0.72, 1.34, 4.08, 3.55, { fillColor: colors.white, lineColor: colors.line, shadow: true });
  addCard(slide, 5.12, 1.34, 4.16, 3.55, { fillColor: colors.white, lineColor: colors.line, shadow: true });
  addTag(slide, 0.96, 1.58, 1.0, "目标", colors.softBlue, colors.blue);
  addTag(slide, 5.36, 1.58, 1.0, "意义", colors.softGold, colors.gold);
  addCardTitle(slide, 0.96, 2.02, 2.6, "本课题希望解决的问题");
  addBulletList(slide, [
    "让商城系统形成完整购物闭环，不停留在“只能看页面”。",
    "让营销活动规则更清楚，避免不同活动之间逻辑混乱。",
    "让后台管理和前台展示联动起来，体现系统整体性。",
  ], 0.98, 2.46, 3.2, 1.8, 13);
  addCardTitle(slide, 5.36, 2.02, 2.4, "做这个系统的实际意义");
  addBulletList(slide, [
    "把前后端分离的商城开发流程完整跑通。",
    "把用户端、活动模块、后台端放到一个项目中统一实现。",
    "为毕业设计答辩展示一个比较完整的中小型电商系统。",
  ], 5.38, 2.46, 3.2, 1.8, 13);
  addFooter(slide, "讲法很简单：为什么做这个系统，它解决了什么问题");
}

// Slide 4 Tech stack
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "技术简介", 3, colors.gold, colors.softGold);
  addText(slide, "这一页不用讲太深，只需要让老师知道：前端怎么做、后端怎么做、数据存在哪里。", {
    x: 0.72,
    y: 1.0,
    w: 8.45,
    h: 0.18,
    fontSize: 12.8,
    color: colors.muted,
  });
  const techs = [
    { x: 0.72, y: 1.44, title: "Vue 3", desc: "前端主框架，用于组织页面和交互逻辑。", fill: colors.softBlue, accent: colors.blue },
    { x: 3.12, y: 1.44, title: "Vant", desc: "移动端组件库，用于用户商城页面开发。", fill: colors.softTeal, accent: colors.teal },
    { x: 5.52, y: 1.44, title: "Element Plus", desc: "后台管理组件库，用于管理端页面开发。", fill: colors.softGold, accent: colors.gold },
    { x: 0.72, y: 3.16, title: "Flask", desc: "后端框架，负责接口、业务逻辑和规则校验。", fill: colors.softCoral, accent: colors.coral },
    { x: 3.12, y: 3.16, title: "SQLAlchemy", desc: "ORM 工具，用于模型定义和数据库操作。", fill: colors.softBlue, accent: colors.blue },
    { x: 5.52, y: 3.16, title: "MySQL", desc: "关系型数据库，负责业务数据持久化存储。", fill: colors.softTeal, accent: colors.teal },
  ];
  techs.forEach((tech) => {
    addCard(slide, tech.x, tech.y, 1.98, 1.32, { fillColor: tech.fill, lineColor: tech.fill });
    addText(slide, tech.title, {
      x: tech.x + 0.18,
      y: tech.y + 0.18,
      w: 1.62,
      h: 0.18,
      fontSize: 17,
      bold: true,
      color: tech.accent,
      align: "center",
    });
    addText(slide, tech.desc, {
      x: tech.x + 0.18,
      y: tech.y + 0.52,
      w: 1.62,
      h: 0.46,
      fontSize: 10.8,
      color: colors.text,
      align: "center",
      valign: "mid",
    });
  });
  addFooter(slide, "一句话总结：前端 Vue，后端 Flask，数据库 MySQL");
}

// Slide 5 Architecture
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "系统总体架构图", 4, colors.blue, colors.softBlue);
  addFigure(slide, figures.architecture, 0.72, 1.28, 5.5, 3.65, "系统总体架构图", "使用 fig3_1_architecture.svg");
  addCard(slide, 6.5, 1.42, 2.78, 0.9, { fillColor: colors.white, lineColor: colors.line, barColor: colors.blue });
  addCard(slide, 6.5, 2.5, 2.78, 0.9, { fillColor: colors.white, lineColor: colors.line, barColor: colors.teal });
  addCard(slide, 6.5, 3.58, 2.78, 0.9, { fillColor: colors.white, lineColor: colors.line, barColor: colors.gold });
  addCardTitle(slide, 6.78, 1.68, 1.9, "前端层");
  addCardTitle(slide, 6.78, 2.76, 1.9, "服务层");
  addCardTitle(slide, 6.78, 3.84, 1.9, "数据层");
  addText(slide, "移动端商城 + PC 后台管理端", { x: 6.78, y: 1.98, w: 2.0, h: 0.16, fontSize: 12, color: colors.muted });
  addText(slide, "Flask 接口、业务逻辑和规则校验", { x: 6.78, y: 3.06, w: 2.1, h: 0.16, fontSize: 12, color: colors.muted });
  addText(slide, "MySQL 统一保存商品、订单、活动等数据", { x: 6.78, y: 4.14, w: 2.15, h: 0.28, fontSize: 12, color: colors.muted });
}

// Slide 6 Function structure
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "系统总体功能结构图", 5, colors.teal, colors.softTeal);
  addFigure(slide, figures.functionStructure, 0.72, 1.28, 5.1, 3.65, "系统功能结构图", "使用 fig3_2_function_structure.svg");
  addCard(slide, 6.08, 1.38, 3.12, 1.0, { fillColor: colors.white, lineColor: colors.line, barColor: colors.blue, shadow: true });
  addCard(slide, 6.08, 2.58, 3.12, 1.0, { fillColor: colors.white, lineColor: colors.line, barColor: colors.teal, shadow: true });
  addCard(slide, 6.08, 3.78, 3.12, 1.0, { fillColor: colors.white, lineColor: colors.line, barColor: colors.gold, shadow: true });
  addCardTitle(slide, 6.36, 1.62, 2.2, "用户端功能");
  addCardTitle(slide, 6.36, 2.82, 2.2, "营销活动功能");
  addCardTitle(slide, 6.36, 4.02, 2.2, "后台管理功能");
  addText(slide, "注册登录、首页浏览、商品详情、购物车、结算、订单和个人中心。", {
    x: 6.36, y: 1.92, w: 2.42, h: 0.32, fontSize: 12, color: colors.muted,
  });
  addText(slide, "优惠券、积分、拼团、秒杀和会员权益等活动规则。", {
    x: 6.36, y: 3.12, w: 2.42, h: 0.28, fontSize: 12, color: colors.muted,
  });
  addText(slide, "商品管理、订单处理、会员管理、活动配置和数据看板。", {
    x: 6.36, y: 4.32, w: 2.42, h: 0.28, fontSize: 12, color: colors.muted,
  });
}

// Slide 7 Checkout flow
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "普通购物流程设计", 6, colors.blue, colors.softBlue);
  addFigure(slide, figures.checkoutFlow, 0.72, 1.34, 5.0, 3.6, "购物车与结算流程图", "使用 fig4_8_checkout_flow.svg");
  addCard(slide, 6.0, 1.36, 3.2, 1.1, { fillColor: colors.white, lineColor: colors.line, barColor: colors.blue, shadow: true });
  addCardTitle(slide, 6.28, 1.64, 2.1, "流程主线");
  addText(slide, "商品浏览 → 加入购物车 → 选择地址 → 优惠结算 → 支付 → 生成订单", {
    x: 6.28, y: 1.98, w: 2.42, h: 0.34, fontSize: 12.5, color: colors.muted,
  });
  addCard(slide, 6.0, 2.74, 3.2, 1.85, { fillColor: colors.white, lineColor: colors.line, barColor: colors.teal, shadow: true });
  addCardTitle(slide, 6.28, 3.02, 2.1, "这一页要讲清楚");
  addBulletList(slide, [
    "基础商城交易流程已经完整跑通。",
    "普通商品结算时可以使用优惠券和积分。",
    "订单生成后还能继续查看订单状态和后续操作。",
  ], 6.28, 3.36, 2.3, 1.02, 12.5);
  addFooter(slide, "这页的重点是说明：系统最基本的商城购物流程已经实现完成");
}

// Slide 8 Group flow
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "拼团流程设计", 7, colors.teal, colors.softTeal);
  addFigure(slide, figures.groupFlow, 0.72, 1.28, 5.1, 3.65, "拼团流程图", "使用 fig4_12_group_flow.svg");
  addMetric(slide, 6.1, 1.36, 1.0, 0.92, "建团", "发起拼团", colors.softBlue, colors.blue);
  addMetric(slide, 7.2, 1.36, 1.0, 0.92, "参团", "输入拼团码", colors.softTeal, colors.teal);
  addMetric(slide, 8.3, 1.36, 1.0, 0.92, "成团", "满足人数", colors.softGold, colors.gold);
  addCard(slide, 6.02, 2.64, 3.2, 2.02, { fillColor: colors.white, lineColor: colors.line, barColor: colors.teal, shadow: true });
  addCardTitle(slide, 6.3, 2.92, 2.0, "拼团规则说明");
  addBulletList(slide, [
    "用户可以发起新团，也可以通过拼团码加入别人的团。",
    "后端会判断人数是否达到要求，再决定是否成团。",
    "订单状态会跟着拼团状态一起变化。",
  ], 6.3, 3.26, 2.36, 1.08, 12.5);
}

// Slide 9 Seckill flow
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "秒杀流程设计", 8, colors.coral, colors.softCoral);
  addFigure(slide, figures.seckillFlow, 0.72, 1.28, 5.1, 3.65, "秒杀流程图", "使用 fig4_14_seckill_flow.svg");
  addMetric(slide, 6.1, 1.36, 1.0, 0.92, "时间", "活动时段", colors.softCoral, colors.coral);
  addMetric(slide, 7.2, 1.36, 1.0, 0.92, "库存", "活动库存", colors.softGold, colors.gold);
  addMetric(slide, 8.3, 1.36, 1.0, 0.92, "限购", "购买限制", colors.softBlue, colors.blue);
  addCard(slide, 6.02, 2.64, 3.2, 2.02, { fillColor: colors.white, lineColor: colors.line, barColor: colors.coral, shadow: true });
  addCardTitle(slide, 6.3, 2.92, 2.0, "秒杀规则说明");
  addBulletList(slide, [
    "秒杀商品下单时要再次判断活动时间、库存和限购数量。",
    "秒杀商品不能和优惠券、积分一起叠加使用。",
    "这样可以避免出现优惠叠加导致金额异常。",
  ], 6.3, 3.26, 2.36, 1.08, 12.5);
}

// Slide 10 Backend link
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "后台管理与前后台联动", 9, colors.blue, colors.softBlue);
  addCard(slide, 0.72, 1.3, 4.32, 3.66, { fillColor: colors.white, lineColor: colors.line, shadow: true, barColor: colors.blue });
  addCardTitle(slide, 1.0, 1.58, 2.4, "后台端主要负责什么");
  addBulletList(slide, [
    "商品管理：维护商品标题、价格、分类、库存和上下架状态。",
    "订单管理：查看订单状态，进行发货等处理。",
    "会员管理：维护用户等级、积分、余额和账号状态。",
    "活动配置：维护优惠券、拼团和秒杀规则。",
    "数据看板：查看销售额、订单量和运营情况。",
  ], 1.0, 1.94, 3.56, 2.2, 12.5);
  addCard(slide, 5.32, 1.3, 3.96, 1.62, { fillColor: colors.softTeal, lineColor: colors.softTeal });
  addCardTitle(slide, 5.62, 1.62, 2.9, "联动关系怎么理解");
  addText(slide, "后台先维护规则，前台再根据接口返回结果动态展示页面内容。活动不是写死在页面里的。", {
    x: 5.62,
    y: 2.0,
    w: 3.1,
    h: 0.5,
    fontSize: 13,
    color: colors.text,
  });
  addCard(slide, 5.32, 3.18, 3.96, 1.78, { fillColor: colors.white, lineColor: colors.line, shadow: true, barColor: colors.teal });
  addCardTitle(slide, 5.62, 3.46, 2.8, "答辩时建议这样讲");
  addBulletList(slide, [
    "前台负责展示。",
    "后台负责配置。",
    "后端负责校验和联动。",
  ], 5.62, 3.8, 2.7, 0.92, 13);
}

// Slide 11 ER
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "数据库 ER 图设计", 10, colors.teal, colors.softTeal);
  addFigure(slide, figures.er, 0.72, 1.24, 5.3, 3.72, "ER 图", "使用 fig3_3_er.svg");
  addCard(slide, 6.28, 1.36, 2.94, 3.46, { fillColor: colors.white, lineColor: colors.line, shadow: true, barColor: colors.teal });
  addCardTitle(slide, 6.56, 1.64, 2.1, "核心实体关系");
  addBulletList(slide, [
    "用户和地址是一对多关系。",
    "用户和订单是一对多关系。",
    "商品既参与普通购买，也参与拼团和秒杀活动。",
    "优惠券分为系统优惠券和用户已领取优惠券。",
    "拼团队伍实体负责记录拼团码和成团状态。",
  ], 6.56, 2.0, 2.2, 2.2, 12.2);
}

// Slide 12 Highlights summary
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "系统设计亮点", 11, colors.gold, colors.softGold);
  addText(slide, "前面几页设计内容可以最后收束成这三点，这样老师更容易记住你的项目特点。", {
    x: 0.72,
    y: 1.0,
    w: 8.5,
    h: 0.2,
    fontSize: 12.8,
    color: colors.muted,
  });
  addCard(slide, 0.78, 1.48, 2.72, 3.1, { fillColor: colors.white, lineColor: colors.line, shadow: true });
  addCard(slide, 3.64, 1.48, 2.72, 3.1, { fillColor: colors.white, lineColor: colors.line, shadow: true });
  addCard(slide, 6.5, 1.48, 2.72, 3.1, { fillColor: colors.white, lineColor: colors.line, shadow: true });
  addMetric(slide, 1.38, 1.82, 1.5, 0.92, "亮点 1", "交易闭环", colors.softBlue, colors.blue);
  addMetric(slide, 4.24, 1.82, 1.5, 0.92, "亮点 2", "规则清楚", colors.softTeal, colors.teal);
  addMetric(slide, 7.1, 1.82, 1.5, 0.92, "亮点 3", "联动明显", colors.softGold, colors.gold);
  addText(slide, "用户可以完成浏览、加购、结算、下单、查看订单这一整条交易流程。", {
    x: 1.06, y: 3.0, w: 2.16, h: 0.72, fontSize: 13, color: colors.text, align: "center",
  });
  addText(slide, "拼团和秒杀规则分开处理，优惠券和积分也能体现不同使用限制。", {
    x: 3.92, y: 3.0, w: 2.16, h: 0.72, fontSize: 13, color: colors.text, align: "center",
  });
  addText(slide, "后台配置活动，前台读取结果，体现出系统不是孤立页面而是整体协同。", {
    x: 6.78, y: 3.0, w: 2.16, h: 0.72, fontSize: 13, color: colors.text, align: "center",
  });
}

// Slides 13-16 screenshot placeholders
addScreenshotPairPage(
  "系统运行界面：首页 + 商品详情",
  12,
  "截图位 01：首页截图",
  "建议放首页主界面。\n最好能看到轮播图、分类入口、商品列表。",
  "截图位 02：商品详情截图",
  "建议放商品详情页。\n最好能看到价格、规格、购买按钮等核心区域。",
  colors.blue
);

addScreenshotPairPage(
  "系统运行界面：购物车 + 结算页",
  13,
  "截图位 03：购物车截图",
  "建议放购物车页面。\n最好能看到勾选、数量调整、合计金额。",
  "截图位 04：结算页截图",
  "建议放结算页。\n最好能看到地址、优惠券、积分、支付区域。",
  colors.teal
);

addScreenshotPairPage(
  "系统运行界面：订单页 + 活动页",
  14,
  "截图位 05：订单页截图",
  "建议放订单列表或订单详情页。\n最好能体现订单状态变化。",
  "截图位 06：拼团页或秒杀页截图",
  "建议放拼团大厅、拼团码页面，或者秒杀活动页。\n优先选能看出活动规则的截图。",
  colors.gold
);

addScreenshotPairPage(
  "系统运行界面：后台首页 + 管理页面",
  15,
  "截图位 07：后台首页 / 数据看板截图",
  "建议放后台看板页。\n最好能看到统计卡片、图表或销售数据。",
  "截图位 08：商品管理页或活动配置页截图",
  "建议放后台业务页面。\n优先选择商品管理、订单管理、拼团配置或秒杀配置。",
  colors.coral
);

// Slide 17 Future work
{
  const slide = pptx.addSlide();
  addPageChrome(slide, "今后待完善的地方", 16, colors.teal, colors.softTeal);
  addText(slide, "这一页不是说项目不好，而是说明你知道系统后面还能继续怎么完善。", {
    x: 0.72,
    y: 1.0,
    w: 8.5,
    h: 0.18,
    fontSize: 12.8,
    color: colors.muted,
  });
  const items = [
    { x: 0.72, y: 1.48, title: "真实支付接入", desc: "后续可接入真实支付接口，让订单支付流程更完整。", fill: colors.softBlue, accent: colors.blue },
    { x: 5.02, y: 1.48, title: "真实物流接入", desc: "后续可接入物流查询接口，让发货和物流跟踪更真实。", fill: colors.softTeal, accent: colors.teal },
    { x: 0.72, y: 3.3, title: "高并发优化", desc: "针对秒杀等场景，可进一步优化并发处理和库存控制。", fill: colors.softGold, accent: colors.gold },
    { x: 5.02, y: 3.3, title: "推荐与搜索优化", desc: "后续可继续完善推荐算法、搜索体验和部署能力。", fill: colors.softCoral, accent: colors.coral },
  ];
  items.forEach((item) => {
    addCard(slide, item.x, item.y, 4.2, 1.42, { fillColor: item.fill, lineColor: item.fill });
    addText(slide, item.title, {
      x: item.x + 0.22,
      y: item.y + 0.24,
      w: 1.7,
      h: 0.18,
      fontSize: 18,
      bold: true,
      color: item.accent,
    });
    addText(slide, item.desc, {
      x: item.x + 0.22,
      y: item.y + 0.62,
      w: 3.66,
      h: 0.42,
      fontSize: 12.5,
      color: colors.text,
    });
  });
}

// Slide 18 Thanks
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.dark };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 10,
    h: 5.625,
    line: { color: colors.dark, width: 0 },
    fill: { color: colors.dark },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: -1.1,
    y: -0.75,
    w: 3.8,
    h: 2.4,
    line: { color: "25405A", width: 0 },
    fill: { color: "25405A", transparency: 18 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 7.6,
    y: 4.35,
    w: 3.2,
    h: 1.8,
    line: { color: "274A67", width: 0 },
    fill: { color: "274A67", transparency: 10 },
  });
  addText(slide, "致谢", {
    x: 0.92,
    y: 1.0,
    w: 2.2,
    h: 0.38,
    fontFace: fonts.title,
    fontSize: 34,
    bold: true,
    color: colors.white,
  });
  addText(slide, "感谢各位老师聆听", {
    x: 0.96,
    y: 2.15,
    w: 4.2,
    h: 0.34,
    fontSize: 28,
    bold: true,
    color: colors.white,
  });
  addText(slide, "恳请各位老师批评指正", {
    x: 0.98,
    y: 2.72,
    w: 3.9,
    h: 0.24,
    fontSize: 18,
    color: "DCE7F2",
  });
  addText(slide, "Thanks For Listening", {
    x: 0.98,
    y: 3.28,
    w: 3.2,
    h: 0.18,
    fontSize: 13,
    italic: true,
    color: "9FB6C8",
  });
  addCard(slide, 6.02, 1.42, 3.1, 2.18, { fillColor: "132A3B", lineColor: "2A475E" });
  addCardTitle(slide, 6.34, 1.78, 1.8, "答辩收尾建议", colors.white);
  addBulletList(slide, [
    "收尾时只说一句感谢，不再展开新内容。",
    "如果老师提问，再回到系统亮点和设计思路回答。",
    "重点记住：购物闭环、活动规则、前后台联动。",
  ], 6.34, 2.18, 2.2, 1.0, 12.5, "DCE7F2");
}

pptx.writeFile({ fileName: outFile }).then(() => {
  console.log(outFile);
}).catch((err) => {
  console.error(err);
  process.exit(1);
});
