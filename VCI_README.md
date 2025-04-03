# How to use

## Installation

follow the instructions given in the comment in `environment.yml` to install both the dependencies and the project itself into a conda environment

## Preparation

1. copy the dataset to `data/vci/<DATASET_NAME>`
2. run the scripts in `scripts/vci` to convert our dataset format to the EasyVolcap format
3. generate masks if not present in the dataset

## Configuration

1. create a dataset config (see `configs/datasets/vci_*` for reference)
2. create an experiment config file (see `configs/exps/vci/*` for reference)

## Preprocessing

run the following to generate the vhulls and surfs

```sh
evc-test -c \
configs/base.yaml,\
configs/models/r4dv.yaml,\
configs/datasets/<DATASET_NAME>/<SCENE_NAME>.yaml,\
configs/specs/optimized.yaml,\
configs/specs/vhulls.yaml
```

```sh
evc-test -c \
configs/base.yaml,\
configs/models/r4dv.yaml,\
configs/datasets/vci/scene_1.yaml,\
configs/specs/optimized.yaml,\
configs/specs/surfs.yaml
```

when prompted, copy the bounds to `datasets/<DATASET_NAME>/<SCENE_NAME>_obj.yaml`

## Training

```sh
evc-train -c \
configs/exps/vci/4k4d_<SCENE_NAME>_r4.yaml \
model_cfg.sampler_cfg.render_gs=True
```

## Render Preprocessing

```sh
python scripts/realtime4dv/charger.py \
--sampler SuperChargedR4DV \
--exp_name 4k4d_<SCENE_NAME> \
-- -c \
configs/exps/vci/4k4d_<SCENE_NAME>_r4.yaml,\
configs/specs/super.yaml
```

## Rendering

Start the rendering GUI

```sh
evc-gui -c \
configs/exps/vci/4k4d_<SCENE_NAME>_r4.yaml,\
configs/specs/superf.yaml \
exp_name=4k4d_<SCENE_NAME>
```
