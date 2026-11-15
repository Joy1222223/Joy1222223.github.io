---
title: Procedural Materials
cover: materials/showcase-rockpath.webp
order: 2
---
## Substance Designer → Unreal Engine

Four fully procedural materials built in **Substance Designer**. Every shape, colour and wear pass is driven by exposed parameters, so one graph can become a whole family of looks — then the maps go into **Unreal Engine** with real geometry displacement.

stats: 4 Materials | 43 Exposed parameters | 2048 px Texture maps | 5 Maps per material

### Parameters in Motion

Move one slider and the whole material rebuilds: stone count, row offset, mortar width, edge wear and colour, rendered frame by frame.

::: switch
Rock Path | materials/params-rockpath.mp4
Bricks | materials/params-bricks.mp4
:::

### Try It Yourself

Pick a material, pick a parameter, and drag. Every position is a real render of the rounded cylinder with that value — the height map changes too, so the displacement follows.

::: params
Rock Path | Stone Count | materials/p/rockpath-stone-count
Rock Path | Row Offset | materials/p/rockpath-row-offset
Rock Path | Stone Size | materials/p/rockpath-stone-size
Rock Path | Overall Hue | materials/p/rockpath-hue
Bricks | Brick Count | materials/p/bricks-brick-count
Bricks | Brick Offset | materials/p/bricks-brick-offset
Bricks | Mortar Width | materials/p/bricks-mortar
Bricks | Brick Hue | materials/p/bricks-hue
Wood | Plank Count | materials/p/wood-plank-count
Wood | Grain Warp | materials/p/wood-grain-warp
Wood | Wood Hue | materials/p/wood-hue
Wood | Saturation | materials/p/wood-saturation
Mud | Water Level | materials/p/mud-water-level
Mud | Mud Mounds | materials/p/mud-mounds
Mud | Mud Flow | materials/p/mud-flow
Mud | Normal Strength | materials/p/mud-normal
:::

### Final Look

Iray renders from Substance Designer, next to the Base Color, Roughness, Height, Normal and AO maps.

::: switch
Rock Path | materials/showcase-rockpath.webp
Bricks | materials/showcase-bricks.webp
Wood | materials/showcase-wood.webp
Mud | materials/showcase-mud.webp
:::

### Node Graphs

::: switch
Rock Path | materials/graph-rockpath.webp
Bricks | materials/graph-bricks.webp
Wood | materials/graph-wood.webp
Mud | materials/graph-mud.webp
:::

### Unreal Material Setup

One master material for all four. Tiling is exposed as Repeat U / V, and the Displacement map is multiplied by the vertex normal and a Height Intensity parameter, then fed into World Position Offset — so every material instance can push its own depth.

![](materials/unreal-material-setup.webp)

## Substance Designer → Substance Painter → Unreal Engine
