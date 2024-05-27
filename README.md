# Fionn AI Project

This README contains the instructions required for configuring and operating the Fionn AI platform. 
Fionn AI is designed for WSI (Whole Slide Image) **Oxford scoring**, featuring a **user-friendly and intuitive interface**. The platform aims to substantially reduce the diagnosis time for IgA Nephropathy by enabling doctors with minimal AI and machine learning experience to utilize advanced diagnostic tools.
Key functionalities include **scoring of entire slide images** and **classification of individual glomeruli**. Additionally, doctors can access a history of analyzed WSIs and view detailed results on the platform.

![image](https://github.com/WladimirLct/Projet_M1/assets/72396636/6fba9dc8-266e-4536-b5e7-4380a7ba5658)


## System Requirements and Dependencies

Ensure you have the following dependencies installed:

1. **Java Environment**
   Install the Java Development Kit (JDK) and Java Runtime Environment (JRE) using:

   ```sh
   sudo apt install default-jdk
   sudo apt install default-jre
   ```

2. **Openslide**
   Install Openslide, a C library that provides a simple interface to read whole-slide images (also known as virtual slides):

   ```sh
   sudo apt-get install openslide-tools
   ```

3. **QuPath**
   Download and install QuPath from the [official releases page](https://github.com/qupath/qupath/releases).

## Python Setup

### Creating a Python Environment

Create and activate a new Conda environment:

```sh
conda create -n FionnAI python=3.10
conda activate FionnAI
```

### Installing Required Libraries

Install the following Python libraries:

1. **Numpy** - For numerical operations:

   ```sh
   pip install numpy
   ```

2. **PyTorch and Torchvision** - For deep learning:

   ```sh
   pip install torch==1.13.1 torchvision==0.14.1 --index-url https://download.pytorch.org/whl/cu117
   ```

3. **Detectron2** - For glomeruli detection:

   ```sh
   python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
   ```

   > Note: Ensure that `nvcc` is uninstalled before this step to avoid version conflicts.

4. **Project Requirements** - Install all other required packages:

   ```sh
   pip install -r requirements.txt
   ```

5. **Paquo** - Modify the configuration:

   Update the `.paquo.toml` file to include your QuPath directory path. Ensure it points to the entire QuPath directory, not just the executable.

## Running Fionn AI

To run the Fionn AI application, follow these steps:

1. Open your terminal and navigate to the root directory of the repository.

2. Ensure the `MESCnn` module is discoverable by setting the Python path:

   ```sh
   export PYTHONPATH=.
   ```

3. Execute the `main.py` script to start the application:

   ```sh
   python main.py
   ```


## Team and Presentation

### Team Composition
Our team consists of 13 students pursuing a Master's degree in Big Data or E-Santé at ISEN Lille:
- Wladimir L
- Antoine M
- Théo H
- Aymane L
- Clément C
- Guillaume C
- Amine B
- Nina T
- Julien L
- Lucile V
- Paul G
- Redouane I
- Yekaterina T

### Supervision & collaboration
The project was guided by:
- Dr. Feryal Windal, Professor
- Bilel Guetarni, PhD. student
  
We received data (Unlabelled and labelled WSIs) from Dr. Jean-Baptiste Gibier, CHU Lille.

### Project Presentation
A presentation detailing the project and its significant performance enhancements is available [here](https://www.canva.com/design/DAGCqcQAijY/YZ-5nyF3BS1NyReTwN4KcQ/edit?utm_content=DAGCqcQAijY&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton).   !!!!! Change it with a view only of the canva !!!!!

### Sources
This project is developed on the foundations provided by the [MESCnn GitHub repository](https://github.com/Nicolik/MESCnn/tree/main).
Our project is designed to assist doctors, who may not have expertise in AI or machine learning, in deriving Oxford scores from their Whole Slide Images (WSIs). Additionally, our repository significantly enhances the processing speed of WSIs by taking advantage of multiprocessing and intelligent filtering of non-informative tiles. A notebook to fine-tune the model on partially labeled WSI is also available (Partially_labeled.ipynb). This script can be used as a foundation to enhance the interface by allowing medical experts to label some glomeruli and fine-tune the model on it so that he can predict the unlabeled gomeruli with a better accuracy.
