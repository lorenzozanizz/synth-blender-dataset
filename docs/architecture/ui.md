# UI Architecture

## Overview

The extension's UI lives entirely in Blender's 3D viewport sidebar under the "Rendersynth" category. The code is in `ext/ui/` and is divided into panels, a pipeline editor, reusable widgets, property definitions, and a labeling sub-panel.

---

## Panels

Three top-level panels are registered:

- **Generator** (`panels.py`) is the main entry point. It exposes output path, file prefix, image count, seed, labeling format selector, and the generate/preview buttons. The labeling format section is drawn by a pluggable `LabelConfigHandler` retrieved from `LabelingConfigRegistry`, so format-specific UI can be added without modifying the panel itself.
- **Settings** (`panels.py`) groups logging configuration: the log directory path, the enable toggle, and buttons to open the log folder or commit the new path.
- **Info** (`panels.py`) displays the extension version, the Blender target version, and links to the repository and documentation.

A separate set of panels for the pipeline editor and the labeling panel are also registered. The pipeline editor panels are managed by `pipe_editor.py` and `pipeline_list_viewer.py`; the labeling panel lives in `ext/ui/labeling/`.

---

## Pipeline editor

The pipeline editor has two main views, switched by `ChangePipelineViewerTabOperator`: a list view showing all currently configured pipes with reorder and remove controls, and a config view showing the editor for the selected pipe.

Each pipe type has a corresponding `PipeDrawer` subclass registered in `OperationDrawerRegistry`. The drawer's `draw_editor` method is called whenever that pipe is selected for editing. Most editors are composed from shared widgets rather than written from scratch, which keeps individual pipe editors short and consistent.

Separately, each pipe type also has a `PipeSchema` subclass registered in `PipeSchemaRegistry`. The schema's `extract_config_from_ui` and `apply_config_to_ui` methods handle serialization of the UI state to and from the JSON config dict stored on the pipe's Blender property. This is how the pipeline survives saving the `.blend` file and how JSON import/export works.

---

## Widgets

`ext/ui/pipe_edit_widgets.py` defines a set of reusable UI components used across multiple pipe editors. Each widget is a class with static `draw`, `extract_data`, `setup_from_config`, and `reset` methods: a consistent interface that the pipe drawers and schemas call into. Examples include:

- `ObjectTargeter` draws the list of targeted scene objects with a capture button.
- `NodeDistributionSelector` draws the distribution editor (either a preset dropdown with parameters, or a node-tree reference for advanced use), adapting to 1D, 2D, or 3D output.
- `AxisTarget` draws x/y/z toggles for selecting which axes a randomization applies to.
- `MaterialSelector`, `PathListSelector`, `PositionListSelector` manage their respective lists with add/remove controls.
- `ConditionalWidget` wraps another widget with an enable checkbox, used where an optional sub-configuration needs to be shown or hidden.

This widget-based approach makes it practical to add new pipes: the editor for a new operation is typically an assembly of existing widgets with at most a handful of new property draws.

---

## Properties

All Blender scene properties used by the extension are declared in `ext/ui/properties.py` and registered onto `bpy.types.Scene` at addon load time. They are organized into three groups: UI/output properties (destination path, seed, amount, format selector, logging path), per-pipe operation properties shared across multiple editors (distribution parameters, axis toggles, captured object lists, node references), and distribution-specific scalar properties (min, max, mean, standard deviation, and so on for each supported distribution shape).

The labeling system has its own property group declarations in `ext/labeling/bpy_properties.py`, registered separately.

---

## Handlers

`ext/ui/handlers.py` registers a `depsgraph_update_post` handler (`sync_distribution_handler`) that runs after each scene update to reconcile the list of `DistributionNodeTree` objects in `bpy.data.node_groups` with the scene-level collection used by the distribution selector UI. This keeps the UI in sync when distribution trees are added, renamed, or deleted outside of the extension's own operators.

---

## Labeling sub-panel

The labeling UI in `ext/ui/labeling/` provides separate sections for class definitions, direct object-to-class assignments, rule-based assignments, and multi-object entity definitions. Each section is rendered as a `UIList` with add/remove operators. The active section is controlled by `SwitchLabelingTabOperator`, which writes to `window_manager['labeling_tab']` and the panel reads this value to decide what to draw.
