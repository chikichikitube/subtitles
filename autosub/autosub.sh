# get docker image for Pytorch for AMD Navi 21 GPUs
docker pull rocm/pytorch:rocm5.2_ubuntu20.04_py3.7_pytorch_1.11.0_navi21

# create drun alias with correct options
alias drun='sudo docker run -it --name autosub --network=host --device=/dev/kfd --device=/dev/dri --group-add=video --ipc=host --cap-add=SYS_PTRACE --security-opt seccomp=unconfined -v $HOME/dockerx:/dockerx -v /mnt/archive/chikichikitube/:/chikichikitube -v /mnt/project/github/chikichiki.tube/:/chikichiki.tube'

# initial drun and creation of container
drun rocm/pytorch:rocm5.2_ubuntu20.04_py3.7_pytorch_1.11.0_navi21

# start and exec container
docker container start autosub && docker exec -it autosub bash

# install software dependencies
sudo apt update && sudo apt -y install ffmpeg
pip3 install git+https://github.com/openai/whisper.git 
pip3 install more-itertools pyyaml pandas
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/rocm5.1.1

# symlink autosub.py script from git and execute
cd /chikichiki.tube/autosub && python3 /chikichiki.tube/autosub/autosub.py