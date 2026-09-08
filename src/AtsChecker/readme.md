## Create environment
```
$ conda create -n ats python=3.12
```
## To activate this environment
```
$ conda activate ats
```
## Install requirements
```
$ pip install -r requirements.txt
```


{
  "s3_path": "s3://ats/cvs/cv2.pdf"
}



uvicorn AtsChecker.client.main:app --reload



python -m AtsChecker.worker