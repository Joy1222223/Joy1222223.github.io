---
title: Substance Designer → Substance Painter → Unreal Engine
cover: painter/cover.webp
---
## Substance Designer → Substance Painter → Unreal Engine

鋼琴場景的材質：先在 **Substance Designer** 程序化製作，主要道具再到 **Substance Painter** 手繪細節，最後在 **Unreal Engine** 組合成完整場景。

stats: 12 種材質 | 12 張節點圖 | 3 個軟體 | 1 個完整場景

![](painter/scene.webp)

## 有機材質

植物和自然表面：仙人掌、苔蘚、葉子、藤蔓、南瓜和花瓣。

### 參數動起來

每個開放的參數從範圍的一端拉到另一端，一格一格渲染出來。

::: switch
有機材質 | painter/params-organic.mp4
:::

### 自己試試看

選一個材質、選一個參數，然後拖動滑桿。每個位置都是用那個數值真實渲染出來的。

::: params
仙人掌 | 斑點顏色 | painter/p/cactus-spot
苔蘚 | 苔蘚色相 | painter/p/moss-hue
南瓜 | 紋路數量 | painter/p/pumpkin-ribs
藤蔓 | 顏色漸層 | painter/p/vine-gradient
藤蔓 | 藤蔓流動 | painter/p/vine-flow
:::

### 最終效果

::: switch
仙人掌 | painter/render-cactus.webp
苔蘚 | painter/render-moss.webp
藤蔓 | painter/render-vine.webp
南瓜 | painter/render-pumpkin.webp
花瓣 | painter/render-petal.webp
:::

### 節點圖

::: switch
仙人掌 | painter/graph-cactus.webp
苔蘚 | painter/graph-moss.webp
葉子 | painter/graph-leaves.webp
藤蔓 | painter/graph-vine.webp
南瓜 | painter/graph-pumpkin.webp
花瓣 | painter/graph-petal.webp
:::

## 非有機材質

鋼琴和周圍的空間：烤漆木頭、琴鍵、銅、玻璃、混凝土和地磚。

### 參數動起來

每個開放的參數從範圍的一端拉到另一端，一格一格渲染出來。

::: switch
非有機材質 | painter/params-hard.mp4
:::

### 自己試試看

選一個材質、選一個參數，然後拖動滑桿。每個位置都是用那個數值真實渲染出來的。

::: params
銅 | 金屬色相 | painter/p/copper-hue
窗戶玻璃 | 窗格數量 | painter/p/glass-panes
混凝土 | 污漬 | painter/p/concrete-stains
混凝土 | 混凝土色相 | painter/p/concrete-hue
地磚 | 地磚數量 | painter/p/tile-tiles
:::

### 最終效果

::: switch
鋼琴 | painter/render-piano.webp
琴鍵 | painter/render-piano-key.webp
銅 | painter/render-copper.webp
玻璃 | painter/render-glass.webp
混凝土 | painter/render-concrete.webp
地磚 | painter/render-tile-ground.webp
:::

### 節點圖

::: switch
鋼琴 | painter/graph-piano.webp
琴鍵 | painter/graph-piano-key.webp
銅 | painter/graph-copper.webp
玻璃 | painter/graph-glass.webp
混凝土 | painter/graph-concrete.webp
地磚 | painter/graph-tile-ground.webp
:::
