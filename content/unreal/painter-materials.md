---
title: Substance Designer → Substance Painter → Unreal Engine
cover: painter/cover.webp
home: yes
order: 3
---
## Substance Designer → Substance Painter → Unreal Engine

Materials for the piano scene, built in **Substance Designer**, hand-finished in **Substance Painter** for the hero props, and assembled in **Unreal Engine**.

stats: 12 Materials | 12 Node graphs | 3 Tools | 1 Final scene

![](painter/scene.webp)

### Old vs New

Drag the line to compare the old, weathered materials with the new, clean pass in Unreal.

::: switch
Piano | compare Old | New: painter/compare/piano-worn.webp | painter/compare/piano-new.webp
Wall | compare Old | New: painter/compare/wall-worn.webp | painter/compare/wall-new.webp
Floor | compare Old | New: painter/compare/floor-worn.webp | painter/compare/floor-new.webp
Window | compare Old | New: painter/compare/window-worn.webp | painter/compare/window-new.webp
Keys | compare Old | New: painter/compare/keys-worn.webp | painter/compare/keys-new.webp
:::

## Organic

Plants and natural surfaces: cactus, moss, leaves, vine, pumpkin and petal.

### Parameters in Motion

Each exposed parameter swept from one end of its range to the other, rendered frame by frame.

::: switch
Organic | painter/params-organic.mp4
:::

### Try It Yourself

Pick a material and a parameter, then drag the slider. Every position is a real render at that value.

::: params
Cactus | Spot Color | painter/p/cactus-spot
Moss | Moss Hue | painter/p/moss-hue
Pumpkin | Rib Count | painter/p/pumpkin-ribs
Vine | Color Gradient | painter/p/vine-gradient
Vine | Vine Flow | painter/p/vine-flow
:::

### Final Look

::: switch
Cactus | painter/render-cactus.webp
Moss | painter/render-moss.webp
Vine | painter/render-vine.webp
Pumpkin | painter/render-pumpkin.webp
Petal | painter/render-petal.webp
:::

### Node Graphs

::: switch
Cactus | painter/graph-cactus.webp
Moss | painter/graph-moss.webp
Leaves | painter/graph-leaves.webp
Vine | painter/graph-vine.webp
Pumpkin | painter/graph-pumpkin.webp
Petal | painter/graph-petal.webp
:::

## Hard Surface

The piano and the room around it: lacquered wood, keys, copper, glass, concrete and floor tiles.

### Parameters in Motion

Each exposed parameter swept from one end of its range to the other, rendered frame by frame.

::: switch
Hard Surface | painter/params-hard.mp4
:::

### Try It Yourself

Pick a material and a parameter, then drag the slider. Every position is a real render at that value.

::: params
Copper | Metal Hue | painter/p/copper-hue
Window Glass | Pane Count | painter/p/glass-panes
Concrete | Stains | painter/p/concrete-stains
Concrete | Concrete Hue | painter/p/concrete-hue
Ground Tile | Tile Count | painter/p/tile-tiles
:::

### Final Look

::: switch
Piano | painter/render-piano.webp
Piano Key | painter/render-piano-key.webp
Copper | painter/render-copper.webp
Glass | painter/render-glass.webp
Concrete | painter/render-concrete.webp
Ground Tile | painter/render-tile-ground.webp
:::

### Node Graphs

::: switch
Piano | painter/graph-piano.webp
Piano Key | painter/graph-piano-key.webp
Copper | painter/graph-copper.webp
Glass | painter/graph-glass.webp
Concrete | painter/graph-concrete.webp
Ground Tile | painter/graph-tile-ground.webp
:::
