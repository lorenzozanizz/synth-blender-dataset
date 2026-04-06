from .names import Labels
from ..core.generation import ExecutionParameters, PipelineExecutor


from bpy.types import Operator

class GenerateOperator(Operator):
    """Main operator that reads the config and runs the render loop"""

    bl_idname = Labels.GENERATE.value
    bl_label = "Generate Dataset"

    @staticmethod
    def extract_relevant_data(context) -> ExecutionParameters:
        scene = context.scene
        return ExecutionParameters(1)

    def execute(self, context):
        """Get all selected nodes"""

        scene = context.scene
        # Deserialized all pipes only ones, preparing for thousands of generations poissbly.
        executor = PipelineExecutor(scene)
        executor.compile_pipeline(scene)

        # Validate
        if not output_dir:
            self.report({'ERROR'}, "Output directory not set")
            return {'CANCELLED'}

        if not scene.pipeline_data.operations:
            self.report({'WARNING'}, "Pipeline is empty")
            return {'CANCELLED'}

        # Create output dir
        os.makedirs(output_dir, exist_ok=True)

        try:
            # Compile pipeline once
            pipeline = PipelineExecutor(scene)
            random.seed(seed_value)

            # Generate frames
            for frame_idx in range(num_samples):

                # Set frame number (for animation if needed)
                scene.frame_set(frame_idx)

                # Apply randomization
                pipeline.execute(scene)

                # Render
                filepath = os.path.join(output_dir, f"render_{frame_idx:04d}.png")
                scene.render.filepath = filepath
                bpy.ops.render.render(write_still=True)

                if frame_idx % 10 == 0:
                    print(f"Generated {frame_idx}/{num_samples}")

            self.report({'INFO'}, f"Successfully generated {num_samples} frames to {output_dir}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Generation failed: {str(e)}")
            return {'CANCELLED'}
