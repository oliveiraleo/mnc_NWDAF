# Public-5G NWDAF

This code was designed to run on the free5GC 5G core and its detailed description is located below.

## Tested Environment Configuration

As the execution environment has many components, the tested working versions of the main ones are listed down below:

### Software

- python: 3.8.10 (works with 3.7.x too)
- pip: 23.3.1
- tensorflow: 2.13.1
- keras: 2.13.1
- flask: 3.0.0
- go: 1.18.10
- free5GC: v3.3.0
- Ubuntu Server 20.04.3

**NOTE:** List updated on December, 2023

### Hardware 

Please, check this [other file here](./VMs-setup.md#requirements)

### Quick comparison between [Kim et al. 2022] and our work

The authors of [[Kim et al. 2022]](https://doi.org/10.1109/ICCE53296.2022.9730290) implemented the NWDAF module and its submodules (MTLF and AnLF) integrated to free5GC, however, they used an image dataset as their ML functionality.

First, a reprodction of [Kim et al. 2022]'s work was made (this README details the environment used in this process). After that, [another ML functionality](./ML_test_code/) closely related to Computer Networks field was implemented. Instead of using an image dataset, a [packet capture dataset](https://github.com/oliveiraleo/mnc_NWDAF/tree/mnc_Public-5G/ML_test_code/dataset) containing 6 captures of 1000 packets each was created. This dataset was used to test the new ML functionality and the instructions to reproduce the environment used for this second phase are located on [this other file here](./VMs-setup.md). 

Currently, the integration between [Kim et al. 2022]'s NWDAF and our ML functionality isn't finished yet, so Keras and TesorFlow are not being used on our experiment.

## Configuring the free5GC

Detailed instructions won't be added here as it isn't in the scope of this document, however as a general advice you should [install](https://free5gc.org/guide/#free5gc-installation-guide) the free5GC project and then follow [these instructions](https://free5gc.org/guide/5-install-ueransim/#5-setting-free5gc-and-ueransim-parameters) configuring the IP address on AMF, SMF and UPF configuration files.

**TIP:** You should change the loopback IPs (127.0.0.x) to the one used by the LAN interface

**NOTE:** This [other repository](https://github.com/oliveiraleo/free5gc-auto-deploy) may help you get started with the free5GC setup

## Install the prerequisites

**NOTE:** In this section the commands are supported on a BASH console

1. Install Python3 and pip
```
sudo apt install python3 python3-pip
pip install --upgrade pip
```

2. Install Python required packages
```
pip install -r requirements.txt
```

3. Install Flask
```
pip install flask
```

4. Install TensorFlow
```
pip install tensorflow
```

**NOTE:** The interoperability between the NWDAF and the ML functionality has not been completed yet, so if you are using a constrained computational environment, you can skip installing tensorflow and it's dependencies

5. Add Go Lang support

**NOTE:** If Go version specified on [the first section](./README.md#tested-environment-configuration) is already installed, skip this step

**TIP:** Check Go version using the command `go version` on console

If another version of Go was previously installed, remove the existing version and install Go 1.18.10 using:
```
sudo rm -rf /usr/local/go
wget https://dl.google.com/go/go1.18.10.linux-amd64.tar.gz
sudo tar -C /usr/local -zxvf go1.18.10.linux-amd64.tar.gz
```
If not, install Go using the commands below:
```
wget https://dl.google.com/go/go1.18.10.linux-amd64.tar.gz
sudo tar -C /usr/local -zxvf go1.18.10.linux-amd64.tar.gz
mkdir -p ~/go/{bin,pkg,src}
# The following assumes that your shell is BASH:
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export GOROOT=/usr/local/go' >> ~/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin:$GOROOT/bin' >> ~/.bashrc
echo 'export GO111MODULE=auto' >> ~/.bashrc
source ~/.bashrc
```

## Install the NWDAF module

### 1. Clone the repository inside the `free5GC` folder
```
cd ~/free5gc/
git clone -b mnc_Public-5G https://github.com/oliveiraleo/mnc_NWDAF.git
```

### 2. Copy the configuration file to the free5GC's `config` folder
```
cp mnc_NWDAF/nwdafcfg.yaml config/.
```

### 3. Load some required Go packages

First, change the working directory to the NWDAF's one

```
cd ~/free5gc/mnc_NWDAF/nwdaf
```
Then load the packages below
```
go mod download github.com/antonfisher/nested-logrus-formatter
go get nwdaf.com/service
go mod download github.com/free5gc/version
```

### 4. Install the NWDAF on free5GC

```
cd ~/free5gc/mnc_NWDAF/nwdaf
go build -o nwdaf nwdaf.go
cd ~/free5gc/
cp -r mnc_NWDAF/nwdaf .
```

## Running the Execution Environment

Execute the components in the following order:
1. 5G Core (free5GC)*
2. go module (nwdaf executable compiled on the previous section)
3. python module
4. temp_requester

\* NRF must be running

### To run NWDAF go module
```
cd ~/free5gc/nwdaf/
./nwdaf
# OR
go run nwdaf.go
```

Now the NWDAF should be running

### To run NWDAF python module
```
cd ~/free5gc/nwdaf/pythonmodule/
python main.py 
```

### To run temp_requester
```
cd ~/free5gc/nwdaf/Temp_Requester/
go run temp_requester.go
```

After that, you should select your number:

- If "1" is selected, MTLF (model training function) is executed.
- Otherwise, "2" is selected, AnLF (analytics function) is executed.
- Then, you can try to select a number which means the dataset number.

Currently, the EMNIST dataset which is in the python module is being used. In Temp_Requester, the image is not transmitted (the data number is transmitted using the json).

## Configuring and Using UERANSIM

### 1. Install UERANSIM

On another machine (different from the free5GC one), run:
```
cd ~
git clone https://github.com/aligungr/UERANSIM
cd UERANSIM
sudo apt install make g++ libsctp-dev lksctp-tools iproute2
sudo snap install cmake --classic
make
```
### 2. Configure the Correct IP Addresses

```
cd ~/UERANSIM
nano config/free5gc-gnb.yaml
```

Find the section below:

```
ngapIp: 127.0.0.1   # gNB's local IP address for N2 Interface (Usually same with local IP)
gtpIp: 127.0.0.1    # gNB's local IP address for N3 Interface (Usually same with local IP)
```
And change `127.0.0.1` to the LAN IP from UERANSIM's machine

Now, on this line:

```
# List of AMF address information
amfConfigs:
  - address: 127.0.0.1
    port: 38412
```

Change `127.0.0.1` to the LAN IP from free5GC's machine

### 3. Add an UE to the core

Use the webconsole for that, the detailed instructions are [located here](https://free5gc.org/guide/5-install-ueransim/#4-use-webconsole-to-add-an-ue)

### 4. To run UERANSIM, use:

```
cd UERANSIM
# gnb
build/nr-gnb -c config/free5gc-gnb.yaml
# ue
sudo build/nr-ue -c config/free5gc-ue.yaml
```

## Installing the Virtual Environment 

To install the virtual test environment, please, refer to the file [VMs-setup.md](./VMs-setup.md)

For more information regarding this second phase, please refer to [this section](./README.md#quick-comparison-between-kim-et-al-2022-and-our-work) and to the file linked above.

<!-- TODO: Finish merging the info below

### NWDAF Structure
NWDAF (Network Data Analytics Function) is consist of two part: 1) go module; 2) python module.

Go module can be run on "nwdaf.go" which located in "nwdaf" folder.

Python module can be run on "main.py" which located in "nwdaf/pythonmodule" folder.

### temp_requester Structure
temp_requester is the requester function which can be using on other NFs. 

If you want to call NWDAF from other NFs, the function in this requester can be used. -->

## Using the ML Functionality

After completing the installation of the environment and capturing packages into files you are ready to begin with the Machine Learning tests

### Reproducing Our Environment

To reproduce our results, just follow the instructions below

#### 1. Load the Execution Environment

If not done yet, clone the repository using

```
git clone -b mnc_Public-5G https://github.com/oliveiraleo/mnc_NWDAF.git
cd mnc_Public-5G
```

Create and load a Python virtual environment

```
python -m venv pyvenv
source pyvenv/bin/activate
pip install -r requirements.txt
```

**NOTE:** The interoperability between the NWDAF and the ML functionality has not been completed yet, so if you are using a constrained computational environment, you can skip installing tensorflow and it's dependencies

Then create the `results` folder

```
cd ML_test_code/
mkdir results
```

#### 2. Run the ML script

```
cd ML_test_code/
python nwdaf_ml.py
```

**NOTE:** The current state of the implementation uses relative paths for interacting with the files on the HDD, this is why you need to enter the `ML_test_code` folder

Now it's only a matter of using the menus to guide the execution. Keep in mind that the two possible flows of execution should be 

- I- Train and save model > Inference; or
- II- Load model > Inference

**NOTE:** The model file is overwriten each time training is executed. The same behavior applies to the files under the `results` folder for each run of the script

### Using Our Environment

Utilizing the implemented environment is straightforward. To incorporate your custom data, place it within the `dataset` folder, with training and inference data allocated to their respective folders bearing the same names

Following the data transfer, if necessary, modify the `labels` list on the 53rd line of the [nwdaf_ml.py](./ML_test_code/nwdaf_ml.py) file. Then run the commands from the [section above](./README.md#reproducing-our-environment)

## Citing this work

If you used our [dataset](./ML_test_code/dataset/) or found the code useful, please, use the citation:

Oliveira, L., Silva, R., Lima, P., Pereira, A., Valadares, J., Silva, E., & Dantas, M. (2024). Análise da Funcionalidade da NWDAF no Core 5G Sobre um Conjunto de Dados. In *Anais do XLII Simpósio Brasileiro de Redes de Computadores e Sistemas Distribuídos*, (pp. 798-811). Porto Alegre: SBC. doi:10.5753/sbrc.2024.1474

Or use the BibTex below:

@inproceedings{sbrc,
 author = {Leonardo Oliveira and Rodrigo Silva and Pedro Lima and Antônio Pereira and Júlia Valadares and Edelberto Silva and Mário Dantas},
 title = {Análise da Funcionalidade da NWDAF no Core 5G Sobre um Conjunto de Dados},
 booktitle = {Anais do XLII Simpósio Brasileiro de Redes de Computadores e Sistemas Distribuídos},
 location = {Niterói/RJ},
 year = {2024},
 issn = {2177-9384},
 pages = {798--811},
 publisher = {SBC},
 address = {Porto Alegre, RS, Brasil},
 doi = {10.5753/sbrc.2024.1474},
 url = {https://sol.sbc.org.br/index.php/sbrc/article/view/29836}
}

## License

The original code from upstream did not explicitly specify any license terms. However, the [work contained in this repository](https://github.com/net-ty/mnc_NWDAF/compare/mnc_Public-5G...oliveiraleo:mnc_NWDAF:mnc_Public-5G) is licensed under the GPLv3, as indicated in the [LICENSE](./LICENSE) file, which is reflected in the notice provided below:

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.