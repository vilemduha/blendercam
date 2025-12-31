# Strategies

## Profile (Cutout)
Cutout a silhouette using an optional offset.

![profile cutout](_static/opProfile.png)

### Options
![](_static/CutoutOptions.png)
- **Cut** - which side of the path to place the Cutter - *Inside, Outside, On Line*
- **Start Point** - which path point to start with
- **Skin** - excess material to leave during Roughing
- **Overshoot**
- **Radius**
  - **Lead-in**
  - **Lead-out**
- **Outlines**
  - **Count**
- **Don't Merge**
---

## Pocket
Mills a pocket in the shape of the selected object.

![pocket](_static/opPocket.png)  

### Options
![](_static/PocketOptions.png)
- **Type**
- **Start Position**
- **Skin**
- **Overshoot**
- **Pocket to Curve**
- **Toolpath**
  - **Stepover**
---

## Drill
Detects circles or squares in any 2D curve and converts these into a drill operation.  Supports peck drilling if layers are enabled.

![drill](_static/opDrill.png)  

### Options
![](_static/DrillOptions.png)
- **Holes On**
---

## **Parallel**
Parallel paths at any angle.

![Parallel](_static/opParallel.png)

### Options
![](_static/ParallelOptions.png)
- **Inverse Milling**
- **Skin**
- **Angle of Paths**
- **Toolpath**
  - **Stepover**
  - **Detail**
---

## Cross
Perpendicular paths at any angle.

![cross](_static/opCross.png)  

### Options
![](_static/CrossOptions.png)
- **Inverse Milling**
- **Skin**
- **Angle of Paths**
- **Toolpath**
  - **Stepover**
  - **Detail**
---

## Block

![block](_static/opBlock.png)  

### Options
![](_static/BlockOptions.png)
- **Inverse Milling**
- **Toolpath**
  - **Stepover**
  - **Detail**
---

## Spiral
Best suited for coins or other circular objects

![spiral](_static/opSpiral.png)  

### Options
![](_static/SpiralOptions.png)
- **Inverse Milling**
- **Toolpath**
  - **Stepover**
  - **Detail**
---

## Circles
Best suited for coins or other circular objects

![circles](_static/opCircle.png)  

### Options
![](_static/CirclesOptions.png)
- **Inverse Milling**
- **Toolpath**
  - **Stepover**
  - **Detail**
---

## Outline Fill

![outline fill](_static/opOutline.png)  

### Options
![](_static/OutlineFillOptions.png)
- **Inverse Milling**
- **Toolpath**
  - **Stepover**
  - **Detail**
---

## Carve
Projects any 2d curve on 3d surface

![carve](https://cloud.githubusercontent.com/assets/648108/12060353/19527cf6-af44-11e5-9de1-27cf1c98a90a.jpg) 

### Options
![](_static/CarveOptions.png)
- **Depth**
- **Skin**
- **Toolpath**
  - **Detail**
---

## Waterline

![waterline](https://cloud.githubusercontent.com/assets/648108/12060351/1316d53a-af44-11e5-8158-31c349a7a265.jpg)

### Options
![](_static/WaterlineOptions.png)
- **Slice Detail**
- **Skin**
- **Project Paths**
- **Fill Between Slices**
- **Toolpath**
  - **Stepover**
---

## Curve to Path

### Options
![](_static/CurveOptions.png)
- **Outlines**
  - **Count**
- **Don't Merge**
---

## Medial Axis

### Options
![](_static/MedialAxisOptions.png)
- **Threshold**
- **Detail Size**
- **Add Pocket**
- **Add Medial Mesh**
---

## **Overview of Principle Strategies**

![Strategy Overview](_static/opOverview.png)
