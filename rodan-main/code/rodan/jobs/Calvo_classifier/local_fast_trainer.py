"""Local Fast Trainer
This is the file for running Calvo Fast Trainer loaclly. Make sure
to have an 'Images' folder with the correct inputs in the same directory.
If not, you can change the values in 'inputs' and 'outputs'.

Simply run `python local_fast_trainer.py` to see the output.
This will call `training_engine_sae.py`.

It should generate 3 files in its current state. A background model,
a Model 0, and a Log File.

If you're running it in a Rodan container, this will be located in code/Rodan/rodan/jobs/Calvo_classifier
If the container is already running, try `docker exec -it [container_name] bash` to run the script without
stopping.
"""

from fast_trainer_lib import CalvoTrainer

def main():

    batch_size = 1
    patch_height = 32
    patch_width = 256
    max_number_of_epochs = 1
    max_samples_per_class = 100

    # Fail if arbitrary layers are not equal before training occurs.
    inputs = {
        "Image": [{"resource_path": "Images/Halifax_Folio_42v.png"}],
        "rgba PNG - Layer 0 (Background)": [
            {"resource_path": "Images/042v_BackgroundForNeumes.png"}
        ],
        "rgba PNG - Layer 1": [{"resource_path": "Images/042v_Neumes.png"}],
        "rgba PNG - Selected regions": [
            {"resource_path": "Images/042v_SelectedRegion.png"}
        ],
    }
    outputs = {
        "Model 0": [{"resource_path": "Images/model0.hdf5"}],
        "Model 1": [{"resource_path": "Images/model1.hdf5"}],
        # "Log File": [{"resource_path": "Images/logfile"}],
    }

    trainer = CalvoTrainer(
        batch_size,
        patch_height,
        patch_width,
        max_number_of_epochs,
        max_samples_per_class,
        inputs,
        outputs,
    )

    trainer.runTrainer()


if __name__ == "__main__":
    main()
