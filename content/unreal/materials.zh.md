---
title: 程序化材質
---
## Substance Designer → Unreal Engine

四個在 **Substance Designer** 中完全程序化製作的材質。每一個形狀、顏色和磨損都由開放的參數控制，同一個節點圖就能變出一整組不同的外觀，再把貼圖帶進 **Unreal Engine**，用真實的幾何位移呈現。

stats: 4 種材質 | 41 個開放參數 | 2048 px 貼圖解析度 | 5 張貼圖／每個材質

### 參數動起來

拖動一個滑桿，整個材質就會重新生成：石塊數量、錯位、灰縫寬度、邊緣磨損和顏色，一格一格渲染出來。

::: switch
石路 | materials/params-rockpath.mp4
磚牆 | materials/params-bricks.mp4
:::

### 自己試試看

選一個材質、選一個參數，然後拖動滑桿。每個位置都是用那個數值真實渲染出來的圓角圓柱，高度貼圖也會跟著改變，所以凹凸會一起變化。

::: params
石路 | 石塊數量 | materials/p/rockpath-stone-count
石路 | 錯位 | materials/p/rockpath-row-offset
石路 | 石塊大小 | materials/p/rockpath-stone-size
石路 | 整體色相 | materials/p/rockpath-hue
磚牆 | 磚塊數量 | materials/p/bricks-brick-count
磚牆 | 錯位 | materials/p/bricks-brick-offset
磚牆 | 灰縫寬度 | materials/p/bricks-mortar
磚牆 | 磚塊色相 | materials/p/bricks-hue
木頭 | 木板數量 | materials/p/wood-plank-count
木頭 | 木紋扭曲 | materials/p/wood-grain-warp
木頭 | 木頭色相 | materials/p/wood-hue
木頭 | 飽和度 | materials/p/wood-saturation
泥巴 | 水位 | materials/p/mud-water-level
泥巴 | 石子數量 | materials/p/mud-pebble-amount
泥巴 | 石子大小 | materials/p/mud-pebble-size
泥巴 | 結霜 | materials/p/mud-frost
:::

### 最終效果

Substance Designer 的 Iray 渲染，旁邊是 Base Color、Roughness、Height、Normal 和 AO 貼圖。

::: switch
石路 | materials/showcase-rockpath.webp
磚牆 | materials/showcase-bricks.webp
木頭 | materials/showcase-wood.webp
泥巴 | materials/showcase-mud.webp
:::

### 節點圖

::: switch
石路 | materials/graph-rockpath.webp
磚牆 | materials/graph-bricks.webp
木頭 | materials/graph-wood.webp
泥巴 | materials/graph-mud.webp
:::

### Unreal 材質設定

四個材質共用一個主材質。貼圖重複次數開放成 Repeat U／V，Displacement 貼圖乘上頂點法線和 Height Intensity 參數，再接到 World Position Offset，讓每個材質實例都能調整自己的凸起深度。

![](materials/unreal-material-setup.webp)

## Substance Designer → Substance Painter → Unreal Engine
