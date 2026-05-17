# Context Restoring

## The problem

Synthetic data generation modifies the scene repeatedly. Over a batch of hundreds or thousands of renders, object positions shift, materials swap, lights change intensity, the camera moves, shader node values fluctuate. If any of those changes were left in place after the batch finished, the `.blend` file would end up in an unknown, partially-randomized state. The user would need to undo everything manually, or — worse — keep a backup copy of the scene before running any generation.

For large scenes this is not a trivial concern. A `.blend` file with high-polygon assets, baked simulations, or many linked libraries can be several gigabytes. Requiring a copy before every run is impractical. Rendersynth therefore takes the position that generation must be a read-only operation from the file's perspective: when the batch finishes, the scene must be byte-for-byte equivalent to what it was before `Generate` was pressed.

This guarantee is implemented through a two-level context manager system that every pipeline operation participates in.

---

## How it works

What follows is a brief description of context mananaging in various aspects of the extension
architecture. 

### Operations and Pipeline execution

Every operation class implements two methods:

- `get_global_context()` returns a context manager that is entered once before the first frame of the batch and exited once after the last. It is responsible for capturing the pre-generation state of whatever the operation targets.
- `get_frame_context()` returns a context manager that is entered and exited once per frame. It handles the finer-grained reset needed between individual renders.

`NestedPipelineContext` collects the global contexts from all compiled operations and manages them as a group. `FrameContext` does the same for frame-level contexts. The execution loop in `Executor.execute` then looks structurally like this:

```
with NestedPipelineContext:
    for each shot:
        with FrameContext:
            execute all operations
            render
        # per-frame state restored
    # global state restored
```

Contexts are exited in reverse registration order (last-registered exits first), matching the natural expectation that the last thing applied is the first thing undone.

If an exception is raised mid-batch — a render error, a missing object, anything — the `with` blocks still exit, and the try/finally in `Executor.execute` ensures `wm.progress_end()` is also called. Scene state restoration is not contingent on the batch completing successfully.

### Writing and labeling

When the orchestrator objects being generation, it merges the pipeline's `FullContext` with a context manager 
extracted from the file writer object (the `IOManager`). The `IOManager` obtains the context manager of its inner `IOStrategy`, returning a 
null (empty) context when no context is specified. This is used for example to temporarily edit the scene's compositor nodes when generating 
depth maps and normal maps. 

---

## What each operation restores

The coverage is broad. Every operation that touches the scene owns a context that brings it back.

**Object transforms** (position, rotation, scale) capture the relevant Euler or vector attribute per target object on enter and restore it on exit. For the `Move` operation and the `BezierLock` camera path, the same `PositionContext` is reused.

**Visibility** is the most thorough of the transform contexts. Hiding an object for render purposes in Blender requires setting multiple independent flags: `hide_render`, `hide_set`, and five ray visibility flags (`visible_camera`, `visible_diffuse`, `visible_glossy`, `visible_shadow`, `visible_transmission`, `visible_volume_scatter`). The `VisibilityContext` captures all eight and restores each one individually. Restoring only `hide_render` and missing the ray flags would corrupt labeling behavior in subsequent runs against the same scene.

**Material assignment** captures the first material slot of each target object and reassigns it on exit. If the object had no material before, the slot is cleared rather than left with whatever was applied.

**Shader node values** (intensity, roughness, metallic, and any node property operation) store the node output's `default_value` before randomization and write it back afterwards.

**Textures** store the `image` reference on the target `ShaderNodeTexImage` node and restore it on exit. Images loaded during generation remain in Blender's datablock system but the node is pointed back at the original.

**Camera focal length** stores `camera.lens` and restores it after each frame.

**Bezier camera lock** is the most structurally involved. When the lock-to-object option is enabled, the operation temporarily adds a `TRACK_TO` constraint to the scene camera. The `BezierLockContext` stores both the camera's initial position and rotation, removes the constraint on exit, and restores both transform values. The constraint itself is created fresh each batch and never left on the camera object.

---

## The offset-mode distinction

Operations that support offset mode — where the sampled value is added to the current property rather than replacing it — require per-frame restoration in addition to the global restore. Without it, the first frame's delta would be added to the property and become the new baseline for the second frame, compounding across the batch.

For these operations, `get_frame_context()` returns the same context object as `get_global_context()`, so the property is snapshotted and restored once per frame. For operations running in absolute (non-offset) mode, `get_frame_context()` returns `None`, meaning `FrameContext` skips them entirely — the global context alone is sufficient since absolute assignment does not accumulate.

---

## What is not restored

The render output files written to disk are, of course, not undone — that is the intended output of the process. The render filepath (`scene.render.filepath`) is temporarily set for each shot but is restored implicitly by the next iteration overwriting it; this is one known exception to the strict restore pattern.

Images loaded into Blender's datablock system by the texture operation (`bpy.data.images.load`) remain loaded after generation. They do not affect scene state in a meaningful way but they do occupy memory until the `.blend` is reloaded or the images are manually purged.
