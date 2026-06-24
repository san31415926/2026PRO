$ErrorActionPreference = 'Stop'

function Get-ColorValue {
    param(
        [int]$R,
        [int]$G,
        [int]$B
    )

    return $R + ($G * 256) + ($B * 65536)
}

function Set-ShapeText {
    param(
        $Shape,
        [string]$Text,
        [int]$FontSize = 20,
        [int]$Color = 0,
        [string]$FontName = 'Microsoft YaHei',
        [bool]$Bold = $false,
        [int]$Alignment = 1
    )

    $Shape.TextFrame.TextRange.Text = $Text
    $Shape.TextFrame.TextRange.Font.Name = $FontName
    $Shape.TextFrame.TextRange.Font.Size = $FontSize
    $Shape.TextFrame.TextRange.Font.Bold = [int]$Bold
    $Shape.TextFrame.TextRange.Font.Color.RGB = $Color
    $Shape.TextFrame.TextRange.ParagraphFormat.Alignment = $Alignment
    $Shape.TextFrame.WordWrap = $true
    $Shape.TextFrame.AutoSize = 0
    $Shape.TextFrame.MarginLeft = 10
    $Shape.TextFrame.MarginRight = 10
    $Shape.TextFrame.MarginTop = 6
    $Shape.TextFrame.MarginBottom = 6
}

function Add-TextBox {
    param(
        $Slide,
        [string]$Text,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height,
        [int]$FontSize = 20,
        [int]$Color = 0,
        [string]$FontName = 'Microsoft YaHei',
        [bool]$Bold = $false,
        [int]$Alignment = 1
    )

    $shape = $Slide.Shapes.AddTextbox(1, $Left, $Top, $Width, $Height)
    $shape.Line.Visible = 0
    $shape.Fill.Visible = 0
    Set-ShapeText -Shape $shape -Text $Text -FontSize $FontSize -Color $Color -FontName $FontName -Bold $Bold -Alignment $Alignment
    $null = $shape
}

function Add-TitleBlock {
    param(
        $Slide,
        [string]$Title,
        [string]$Subtitle = '',
        [int]$AccentColor,
        [int]$TextColor
    )

    $bar = $Slide.Shapes.AddShape(1, 28, 24, 10, 42)
    $bar.Fill.ForeColor.RGB = $AccentColor
    $bar.Line.Visible = 0

    Add-TextBox -Slide $Slide -Text $Title -Left 48 -Top 20 -Width 760 -Height 40 -FontSize 26 -Color $TextColor -Bold $true

    if ($Subtitle) {
        Add-TextBox -Slide $Slide -Text $Subtitle -Left 48 -Top 56 -Width 820 -Height 24 -FontSize 10 -Color (Get-ColorValue 107 114 128)
    }
}

function Add-ContentBox {
    param(
        $Slide,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height,
        [int]$FillColor,
        [int]$LineColor
    )

    $shape = $Slide.Shapes.AddShape(1, $Left, $Top, $Width, $Height)
    $shape.Fill.ForeColor.RGB = $FillColor
    $shape.Line.ForeColor.RGB = $LineColor
    $shape.Line.Weight = 1.25
    return $shape
}

function Add-BulletPanel {
    param(
        $Slide,
        [string[]]$Lines,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height,
        [int]$TextColor,
        [int]$FillColor,
        [int]$LineColor
    )

    $panel = Add-ContentBox -Slide $Slide -Left $Left -Top $Top -Width $Width -Height $Height -FillColor $FillColor -LineColor $LineColor
    $text = ($Lines | ForEach-Object { "• $_" }) -join "`n"
    Set-ShapeText -Shape $panel -Text $text -FontSize 18 -Color $TextColor
    $null = $panel
}

function Add-ImageOrPlaceholder {
    param(
        $Slide,
        [string]$Path,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height,
        [string]$Title,
        [string]$Hint,
        [int]$AccentColor
    )

    if (Test-Path -LiteralPath $Path) {
        try {
            $picture = $Slide.Shapes.AddPicture($Path, $false, $true, $Left, $Top, $Width, $Height)
            $null = $picture
            return
        } catch {
        }
    }

    $placeholder = $Slide.Shapes.AddShape(1, $Left, $Top, $Width, $Height)
    $placeholder.Fill.ForeColor.RGB = (Get-ColorValue 246 248 252)
    $placeholder.Line.ForeColor.RGB = $AccentColor
    $placeholder.Line.DashStyle = 4
    $placeholder.Line.Weight = 1.5
    Set-ShapeText -Shape $placeholder -Text "$Title`n`n$Hint" -FontSize 18 -Color (Get-ColorValue 66 74 94) -Bold $true -Alignment 2
    $null = $placeholder
}

function Add-ScreenshotPlaceholder {
    param(
        $Slide,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height,
        [string]$Label,
        [string]$Hint,
        [int]$AccentColor
    )

    Add-ImageOrPlaceholder -Slide $Slide -Path '' -Left $Left -Top $Top -Width $Width -Height $Height -Title $Label -Hint $Hint -AccentColor $AccentColor
}

function Add-Tag {
    param(
        $Slide,
        [string]$Text,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [int]$FillColor,
        [int]$TextColor
    )

    $shape = $Slide.Shapes.AddShape(5, $Left, $Top, $Width, 22)
    $shape.Fill.ForeColor.RGB = $FillColor
    $shape.Line.Visible = 0
    Set-ShapeText -Shape $shape -Text $Text -FontSize 10 -Color $TextColor -Bold $true -Alignment 2
    $null = $shape
}

$root = Split-Path -Parent $PSScriptRoot
$outputPath = Join-Path $root 'defense_ppt_zhangjie.pptx'

if (Test-Path -LiteralPath $outputPath) {
    Remove-Item -LiteralPath $outputPath -Force
}

$accent = Get-ColorValue 25 90 184
$accentLight = Get-ColorValue 232 240 252
$accentSoft = Get-ColorValue 241 245 253
$textPrimary = Get-ColorValue 33 40 53
$textMuted = Get-ColorValue 97 105 122
$lineSoft = Get-ColorValue 204 214 234
$success = Get-ColorValue 56 127 80
$warning = Get-ColorValue 177 108 22

$ppt = $null
$presentation = $null

try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $presentation = $ppt.Presentations.Add()
    $presentation.PageSetup.SlideWidth = 960
    $presentation.PageSetup.SlideHeight = 540

    $slide = $presentation.Slides.Add(1, 12)
    $bg = $slide.Shapes.AddShape(1, 0, 0, 960, 540)
    $bg.Fill.ForeColor.RGB = (Get-ColorValue 249 251 255)
    $bg.Line.Visible = 0
    $hero = $slide.Shapes.AddShape(1, 0, 0, 960, 120)
    $hero.Fill.ForeColor.RGB = $accent
    $hero.Line.Visible = 0
    Add-TextBox -Slide $slide -Text '基于 Python 和 Vue 的数码电子商城的设计与实现' -Left 60 -Top 78 -Width 760 -Height 48 -FontSize 28 -Color (Get-ColorValue 255 255 255) -Bold $true
    Add-TextBox -Slide $slide -Text '毕业设计答辩 PPT' -Left 62 -Top 42 -Width 220 -Height 24 -FontSize 12 -Color (Get-ColorValue 214 228 255)

    $infoCard = $slide.Shapes.AddShape(5, 60, 164, 840, 278)
    $infoCard.Fill.ForeColor.RGB = (Get-ColorValue 255 255 255)
    $infoCard.Line.ForeColor.RGB = $lineSoft
    $infoCard.Line.Weight = 1.25
    $coverInfo = @"
姓名：张捷
学号：202235020346
学院：人工智能学院
专业班级：软件工程 2022-3班
指导教师：侯爱民
答辩时间：2026年4月16日 10:30
答辩地点：3B411
"@
    Set-ShapeText -Shape $infoCard -Text $coverInfo -FontSize 20 -Color $textPrimary
    Add-Tag -Slide $slide -Text '答辩封面' -Left 744 -Top 184 -Width 112 -FillColor $accentLight -TextColor $accent
    Add-TextBox -Slide $slide -Text '突出系统实现亮点，控制讲解节奏，截图后续可自行替换。' -Left 60 -Top 470 -Width 600 -Height 24 -FontSize 11 -Color $textMuted

    $slide = $presentation.Slides.Add(2, 12)
    Add-TitleBlock -Slide $slide -Title '课题背景与研究目标' -Subtitle '围绕问题、目标和实现方向快速交代，不展开论文式铺垫。' -AccentColor $accent -TextColor $textPrimary
    Add-BulletPanel -Slide $slide -Lines @(
        '购物流程需要从商品浏览、加购结算到订单处理形成完整闭环。',
        '营销活动不能只停留在页面展示，规则协同和状态流转需要后端支撑。',
        '后台管理不仅要维护商品与订单，还应支持活动配置与基础运营分析。'
    ) -Left 44 -Top 104 -Width 408 -Height 182 -TextColor $textPrimary -FillColor $accentSoft -LineColor $lineSoft
    Add-BulletPanel -Slide $slide -Lines @(
        '构建一个基于 Python 与 Vue 的数码电子商城系统。',
        '实现用户端、营销活动模块与后台管理端协同运行。',
        '通过测试验证系统交易链路与营销规则能够稳定执行。'
    ) -Left 476 -Top 104 -Width 440 -Height 182 -TextColor $textPrimary -FillColor (Get-ColorValue 252 250 245) -LineColor (Get-ColorValue 232 221 191)
    Add-Tag -Slide $slide -Text '问题导向' -Left 56 -Top 92 -Width 80 -FillColor $accentLight -TextColor $accent
    Add-Tag -Slide $slide -Text '研究目标' -Left 488 -Top 92 -Width 80 -FillColor (Get-ColorValue 255 243 216) -TextColor $warning
    $goalMap = Add-ContentBox -Slide $slide -Left 44 -Top 318 -Width 872 -Height 166 -FillColor (Get-ColorValue 255 255 255) -LineColor $lineSoft
    $goalMapText = @"
核心主线：
商品浏览与交易闭环  →  营销活动规则联动  →  后台配置与运营支撑

答辩口径：
本课题不仅实现了基本商城交易流程，还把优惠券、拼团、秒杀等规则放到统一系统中协同处理，
并通过后台配置与测试验证，体现出较完整的项目实现能力。
"@
    Set-ShapeText -Shape $goalMap -Text $goalMapText -FontSize 18 -Color $textPrimary

    $slide = $presentation.Slides.Add(3, 12)
    Add-TitleBlock -Slide $slide -Title '系统总体架构' -Subtitle '前后端分离架构，突出用户端、后台端、接口服务与数据库协同关系。' -AccentColor $accent -TextColor $textPrimary
    Add-ImageOrPlaceholder -Slide $slide -Path (Join-Path $root 'fig3_1_architecture.svg') -Left 42 -Top 94 -Width 566 -Height 366 -Title '系统架构图' -Hint '若 SVG 无法自动插入，可手动替换为导出图片。' -AccentColor $accent
    Add-BulletPanel -Slide $slide -Lines @(
        '移动端用户商城：负责商品浏览、购物车、结算、订单与活动参与。',
        'PC 后台管理端：负责商品维护、订单处理、会员管理、活动配置与数据看板。',
        'Flask 后端接口：统一处理业务逻辑、规则校验与接口响应。',
        'MySQL 数据库：完成用户、商品、订单、活动与配置数据持久化。'
    ) -Left 632 -Top 108 -Width 284 -Height 244 -TextColor $textPrimary -FillColor $accentSoft -LineColor $lineSoft
    Add-Tag -Slide $slide -Text '图示可复用：fig3_1_architecture.svg' -Left 632 -Top 370 -Width 220 -FillColor $accentLight -TextColor $accent
    Add-TextBox -Slide $slide -Text '讲述重点：前端负责展示与交互，后端负责规则与状态，数据库负责记录与支撑。' -Left 632 -Top 408 -Width 284 -Height 46 -FontSize 14 -Color $textMuted

    $slide = $presentation.Slides.Add(4, 12)
    Add-TitleBlock -Slide $slide -Title '功能模块设计' -Subtitle '按用户端、营销活动与后台管理三块展开，避免逐页念功能。' -AccentColor $accent -TextColor $textPrimary
    Add-ImageOrPlaceholder -Slide $slide -Path (Join-Path $root 'fig3_2_function_structure.svg') -Left 42 -Top 92 -Width 530 -Height 382 -Title '功能结构图' -Hint '优先使用现有功能结构图。' -AccentColor $accent
    Add-BulletPanel -Slide $slide -Lines @(
        '用户端核心功能：注册登录、商品浏览、商品详情、购物车结算、订单与个人中心。',
        '营销活动功能：优惠券与积分、拼团、秒杀、会员权益联动。',
        '后台管理功能：数据看板、商品管理、订单管理、会员管理、活动配置。'
    ) -Left 596 -Top 112 -Width 320 -Height 214 -TextColor $textPrimary -FillColor (Get-ColorValue 255 255 255) -LineColor $lineSoft
    $tri = Add-ContentBox -Slide $slide -Left 596 -Top 352 -Width 320 -Height 122 -FillColor $accentSoft -LineColor $lineSoft
    Set-ShapeText -Shape $tri -Text "答辩讲法：`n先概览整体模块，再立刻转入核心亮点，`n不要把每个功能都讲成流水账。" -FontSize 18 -Color $textPrimary

    $slide = $presentation.Slides.Add(5, 12)
    Add-TitleBlock -Slide $slide -Title '系统核心亮点' -Subtitle '这一页只保留一句主结论和三条亮点，不做面面俱到的功能罗列。' -AccentColor $accent -TextColor $textPrimary
    $heroPanel = Add-ContentBox -Slide $slide -Left 44 -Top 98 -Width 872 -Height 72 -FillColor $accent -LineColor $accent
    Set-ShapeText -Shape $heroPanel -Text '本系统在传统商城交易链路基础上，进一步实现了营销规则联动和前后台协同配置。' -FontSize 24 -Color (Get-ColorValue 255 255 255) -Bold $true -Alignment 2

    $card1 = Add-ContentBox -Slide $slide -Left 44 -Top 202 -Width 264 -Height 198 -FillColor (Get-ColorValue 255 255 255) -LineColor $lineSoft
    Set-ShapeText -Shape $card1 -Text "普通商品结算`n`n支持优惠券与积分抵扣，`n并根据会员等级进行价格计算。" -FontSize 22 -Color $textPrimary -Bold $true -Alignment 2
    Add-Tag -Slide $slide -Text '亮点 01' -Left 124 -Top 378 -Width 100 -FillColor $accentLight -TextColor $accent

    $card2 = Add-ContentBox -Slide $slide -Left 348 -Top 202 -Width 264 -Height 198 -FillColor (Get-ColorValue 255 255 255) -LineColor $lineSoft
    Set-ShapeText -Shape $card2 -Text "拼团状态流转`n`n支持建团、参团、成团，`n通过拼团码与订单状态联动。" -FontSize 22 -Color $textPrimary -Bold $true -Alignment 2
    Add-Tag -Slide $slide -Text '亮点 02' -Left 428 -Top 378 -Width 100 -FillColor $accentLight -TextColor $accent

    $card3 = Add-ContentBox -Slide $slide -Left 652 -Top 202 -Width 264 -Height 198 -FillColor (Get-ColorValue 255 255 255) -LineColor $lineSoft
    Set-ShapeText -Shape $card3 -Text "秒杀规则校验`n`n支持时间、库存、限购判断，`n并明确禁止优惠叠加。" -FontSize 22 -Color $textPrimary -Bold $true -Alignment 2
    Add-Tag -Slide $slide -Text '亮点 03' -Left 732 -Top 378 -Width 100 -FillColor $accentLight -TextColor $accent

    Add-TextBox -Slide $slide -Text '答辩建议：这三点只点到为止，下一页选择一个主打模块讲透即可。' -Left 44 -Top 444 -Width 560 -Height 26 -FontSize 12 -Color $textMuted

    $slide = $presentation.Slides.Add(6, 12)
    Add-TitleBlock -Slide $slide -Title '亮点实现：营销规则联动' -Subtitle '建议主打秒杀或拼团其中之一，如时间允许再补另一项。' -AccentColor $accent -TextColor $textPrimary
    Add-ImageOrPlaceholder -Slide $slide -Path (Join-Path $root 'fig4_12_group_flow.svg') -Left 44 -Top 96 -Width 408 -Height 250 -Title '拼团流程图' -Hint '优先复用 fig4_12_group_flow.svg' -AccentColor $accent
    Add-ImageOrPlaceholder -Slide $slide -Path (Join-Path $root 'fig4_14_seckill_flow.svg') -Left 502 -Top 96 -Width 414 -Height 250 -Title '秒杀流程图' -Hint '优先复用 fig4_14_seckill_flow.svg' -AccentColor $accent
    Add-BulletPanel -Slide $slide -Lines @(
        '前端负责展示商品状态、价格差异与活动入口。',
        '后端负责秒杀时间、库存、限购、拼团码等规则校验。',
        '数据库负责记录队伍状态、订单状态、优惠券状态与库存变化。'
    ) -Left 44 -Top 378 -Width 872 -Height 116 -TextColor $textPrimary -FillColor (Get-ColorValue 255 255 255) -LineColor $lineSoft

    $slide = $presentation.Slides.Add(7, 12)
    Add-TitleBlock -Slide $slide -Title '业务闭环展示' -Subtitle '用一页证明系统不是单点功能，而是具备完整交易链路。' -AccentColor $accent -TextColor $textPrimary
    $flow = Add-ContentBox -Slide $slide -Left 44 -Top 94 -Width 872 -Height 82 -FillColor $accentSoft -LineColor $lineSoft
    Set-ShapeText -Shape $flow -Text '商品浏览  →  商品详情  →  加入购物车/下单  →  结算支付  →  订单生成  →  后台发货  →  用户确认收货/评价' -FontSize 22 -Color $textPrimary -Bold $true -Alignment 2
    Add-ScreenshotPlaceholder -Slide $slide -Left 44 -Top 218 -Width 268 -Height 222 -Label '截图占位 01' -Hint '首页 / 商品详情`n建议保留商品标签、价格和按钮。' -AccentColor $accent
    Add-ScreenshotPlaceholder -Slide $slide -Left 346 -Top 218 -Width 268 -Height 222 -Label '截图占位 02' -Hint '购物车 / 结算页`n建议体现优惠券、积分、地址、支付。' -AccentColor $accent
    Add-ScreenshotPlaceholder -Slide $slide -Left 648 -Top 218 -Width 268 -Height 222 -Label '截图占位 03' -Hint '订单页 / 物流页`n建议体现订单状态与后续操作。' -AccentColor $accent
    Add-TextBox -Slide $slide -Text '截图统一要求：只截核心区域，不保留过多空白；优先选择有数据、有状态变化、有按钮的页面。' -Left 44 -Top 460 -Width 872 -Height 24 -FontSize 11 -Color $textMuted

    $slide = $presentation.Slides.Add(8, 12)
    Add-TitleBlock -Slide $slide -Title '后台管理与前后台联动' -Subtitle '说明活动规则不是写死在前端页面中，而是由后台统一维护。' -AccentColor $accent -TextColor $textPrimary
    Add-BulletPanel -Slide $slide -Lines @(
        '商品管理：维护标题、价格、库存、封面图与上下架状态。',
        '订单管理：查看订单、执行发货、更新物流状态。',
        '会员管理：维护会员等级、积分、余额和账号状态。',
        '活动配置：维护优惠券、拼团规则、秒杀时间与库存。',
        '数据看板：展示销售额、订单量、会员量与图表统计。'
    ) -Left 44 -Top 98 -Width 410 -Height 240 -TextColor $textPrimary -FillColor (Get-ColorValue 255 255 255) -LineColor $lineSoft
    Add-ScreenshotPlaceholder -Slide $slide -Left 490 -Top 108 -Width 194 -Height 226 -Label '截图占位 A' -Hint '数据看板页`n优先选择有图表和统计卡片的画面。' -AccentColor $accent
    Add-ScreenshotPlaceholder -Slide $slide -Left 722 -Top 108 -Width 194 -Height 226 -Label '截图占位 B' -Hint '活动配置 / 订单管理页`n体现后台联动与可配置性。' -AccentColor $accent
    $linkBox = Add-ContentBox -Slide $slide -Left 44 -Top 368 -Width 872 -Height 118 -FillColor $accentSoft -LineColor $lineSoft
    Set-ShapeText -Shape $linkBox -Text "重点强调：`n活动规则先由后台维护，再由前端在页面加载时动态读取；`n这样既能体现前后台协同设计，也便于答辩现场快速调整展示效果。" -FontSize 20 -Color $textPrimary

    $slide = $presentation.Slides.Add(9, 12)
    Add-TitleBlock -Slide $slide -Title '系统测试与结果' -Subtitle '不展示全部测试编号，重点说明覆盖范围、验证方式和结论。' -AccentColor $accent -TextColor $textPrimary
    Add-BulletPanel -Slide $slide -Lines @(
        '测试方式：后端 pytest 接口测试 + 前端手工功能验证。',
        '覆盖内容：注册登录、商品浏览、购物车、下单、优惠券、拼团、秒杀、后台管理。',
        '验证重点：交易链路、营销规则、异常场景与后台运维能力。'
    ) -Left 44 -Top 96 -Width 400 -Height 172 -TextColor $textPrimary -FillColor $accentSoft -LineColor $lineSoft

    $result = Add-ContentBox -Slide $slide -Left 476 -Top 96 -Width 440 -Height 172 -FillColor (Get-ColorValue 255 255 255) -LineColor $lineSoft
    $resultText = @"
测试结论：
• 核心交易流程能够稳定运行。
• 营销规则能够正确执行和校验。
• 后台功能能够支撑基础运营需求。
• 异常场景具备合理拦截与提示。
"@
    Set-ShapeText -Shape $result -Text $resultText -FontSize 20 -Color $textPrimary

    $verify = Add-ContentBox -Slide $slide -Left 44 -Top 300 -Width 872 -Height 186 -FillColor (Get-ColorValue 255 255 255) -LineColor $lineSoft
    $verifyText = @"
答辩口径：
本系统既验证了正常业务流程，也验证了重复注册、库存不足、优惠券重复领取、
秒杀商品违规抵扣、超出限购和余额不足等异常情况，说明系统不仅能“跑通”，
也具备一定的规则控制和容错能力。
"@
    Set-ShapeText -Shape $verify -Text $verifyText -FontSize 22 -Color $textPrimary

    $slide = $presentation.Slides.Add(10, 12)
    Add-TitleBlock -Slide $slide -Title '总结与展望' -Subtitle '收束到“做成了什么”和“后续还能做什么”，不再扩展新信息。' -AccentColor $accent -TextColor $textPrimary
    $sumBox = Add-ContentBox -Slide $slide -Left 44 -Top 98 -Width 872 -Height 128 -FillColor $accent -LineColor $accent
    $sumText = @"
总结：
已完成数码电子商城主要业务功能，实现了用户端、营销活动与后台管理的协同运行。
系统不仅具备基本交易能力，也具备一定的活动运营和后台支撑能力。
"@
    Set-ShapeText -Shape $sumBox -Text $sumText -FontSize 24 -Color (Get-ColorValue 255 255 255) -Bold $true -Alignment 2

    Add-BulletPanel -Slide $slide -Lines @(
        '支付与物流接口可进一步接入真实服务，提升系统真实性。',
        '推荐算法、并发处理与部署优化仍有继续完善空间。'
    ) -Left 44 -Top 266 -Width 540 -Height 144 -TextColor $textPrimary -FillColor (Get-ColorValue 255 255 255) -LineColor $lineSoft

    $qa = Add-ContentBox -Slide $slide -Left 620 -Top 266 -Width 296 -Height 144 -FillColor $accentSoft -LineColor $lineSoft
    Set-ShapeText -Shape $qa -Text "答问提醒：`n先停 1-2 秒，`n先讲结论，再补原因。`n评委愿意听再展开。" -FontSize 22 -Color $textPrimary -Bold $true -Alignment 2
    Add-TextBox -Slide $slide -Text '可选：若你想用致谢页收尾，可在此基础上自行追加一页“感谢各位老师指导”。' -Left 44 -Top 448 -Width 620 -Height 24 -FontSize 11 -Color $textMuted

    $presentation.SaveAs($outputPath, 24)
    $presentation.Close()
    $ppt.Quit()
} finally {
    if ($presentation) {
        try { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) } catch {}
    }
    if ($ppt) {
        try { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) } catch {}
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

Write-Output "Generated: $outputPath"
