---
title: Substance Designer → Substance Painter → Unreal Engine
cover: painter/cover.webp
home: yes
order: 3
---
Materials for the piano scene, built in **Substance Designer**, hand-finished in **Substance Painter** for the hero props, and assembled in **Unreal Engine**.

stats: 12 Materials | 12 Node graphs | 3 Tools | 1 Final scene

![](painter/scene.webp)

### New vs Old

Drag the line to compare the new, clean pass with the old, weathered materials in Unreal.

::: switch
Piano | compare New | Old: painter/compare/piano-new.webp | painter/compare/piano-worn.webp
Wall | compare New | Old: painter/compare/wall-new.webp | painter/compare/wall-worn.webp
Floor | compare New | Old: painter/compare/floor-new.webp | painter/compare/floor-worn.webp
Window | compare New | Old: painter/compare/window-new.webp | painter/compare/window-worn.webp
Keys | compare New | Old: painter/compare/keys-new.webp | painter/compare/keys-worn.webp
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
Cactus | Cactus Hue | painter/p/cactus-hue
Cactus | Highlight | painter/p/cactus-highlight
Cactus | Spot Color | painter/p/cactus-spot
Leaves | Freshness | painter/p/leaves-freshness
Leaves | Saturation | painter/p/leaves-saturation
Leaves | Paleness | painter/p/leaves-paleness
Moss | Moss Opacity | painter/p/moss-opacity
Moss | Greenness | painter/p/moss-green
Moss | Moss Hue | painter/p/moss-hue
Pumpkin | Rib Count | painter/p/pumpkin-ribs
Pumpkin | Ripeness | painter/p/pumpkin-ripeness
Pumpkin | Stripes | painter/p/pumpkin-stripes
Vine | Color Gradient | painter/p/vine-gradient
Vine | Vine Flow | painter/p/vine-flow
Vine | Patchiness | painter/p/vine-patch
Petal | Petal Hue | painter/p/petal-hue
Petal | Edge Tint | painter/p/petal-edge
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
Piano | Ornament Size | painter/p/piano-ornament
Piano | Carving Softness | painter/p/piano-carving
Piano Key | Key Tone | painter/p/keys-tone
Copper | Metal Hue | painter/p/copper-hue
Window Glass | Pane Count | painter/p/glass-panes
Window Glass | Color Variation | painter/p/glass-variation
Concrete | Stains | painter/p/concrete-stains
Concrete | Concrete Hue | painter/p/concrete-hue
Concrete | Warm Patches | painter/p/concrete-warm
Ground Tile | Tile Count | painter/p/tile-tiles
Ground Tile | Dirt | painter/p/tile-dirt
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
