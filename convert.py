import os

datafolder = "data"

for f in os.listdir(datafolder):
    full_path = os.path.join(datafolder, f)
    if full_path.endswith(".pdf"):
        out_path = full_path[:-4]+".html"
        os.system(f"java -jar tika.jar {full_path} >> {out_path}")
