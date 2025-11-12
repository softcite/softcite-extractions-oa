# Softcite Project – TACC Usage Catalogue

**System:** Stampede3 Supercomputer – Texas Advanced Computing Center (TACC)  
**Project:** Softcite – Software Citation Data Processing and Analysis  
**Maintained by:** Softcite Research Team, UT Austin  

---

## 1. Overview

The **Softcite project** uses TACC’s Stampede3 cluster to process and analyze large-scale scientific publication data.  
This guide describes how we use TACC for data preprocessing, job submission, and output monitoring.

---

## 2. Accessing TACC

### Login from Terminal (PowerShell or Git Bash)

```bash
ssh -o MACs=hmac-sha2-256 USERNAME@login3.stampede3.tacc.utexas.edu
```

Replace `USERNAME` with your own TACC login.

On first login, SSH keys will be created at:
```
~/.ssh/id_ed25519
~/.ssh/id_ed25519.pub
```

---

## 3. File Management

### Upload data to TACC (`scp` command)

Upload to home directory:
```bash
scp -r "/c/Users/ExampleUser/Downloads/subset" USERNAME@stampede3.tacc.utexas.edu:~/
```

Upload to scratch (recommended for large datasets):
```bash
scp -r "/c/Users/ExampleUser/Downloads/full_dataset" USERNAME@stampede3.tacc.utexas.edu:/scratch/10000/USERNAME/
```

---

### Download data from TACC

```bash
scp USERNAME@stampede3.tacc.utexas.edu:/scratch/10000/USERNAME/output/*.parquet "/c/Users/ExampleUser/Downloads/"
```

---

### File operations after SSH login

```bash
cd /scratch/10000/USERNAME/
ls -lh
mkdir new_folder
rm old_file.parquet
```

To edit a script:
```bash
nano script.py
```
Save with **Ctrl+O**, exit with **Ctrl+X**.

---

## 4. Running Jobs on Compute Nodes (SLURM)

We do **not** run heavy jobs on login nodes.  
Use SLURM batch scripts for compute work.

### Example: `run_softcite.slurm`

```bash
#!/bin/bash
#SBATCH -J softcite_job
#SBATCH -o softcite_job.out
#SBATCH -e softcite_job.err
#SBATCH -p normal
#SBATCH -N 1
#SBATCH -n 4
#SBATCH -t 02:00:00
#SBATCH -A IRI25022

cd /scratch/10000/USERNAME/
module load python3
python rewrite_mentions_parquet.py
```

Submit:
```bash
sbatch run_softcite.slurm
```

Monitor:
```bash
squeue -u USERNAME
```

Cancel a job:
```bash
scancel JOB_ID
```

---

## 5. Checking Job Outputs

SLURM automatically creates:

- `softcite_job.out` → main output  
- `softcite_job.err` → error logs

Check them:
```bash
cat softcite_job.out
cat softcite_job.err
```

Live updates:
```bash
tail -f softcite_job.out
```

---

## 6. Using `idev` for Interactive Jobs

For testing small scripts interactively:

```bash
idev
cd /scratch/10000/USERNAME/
python test_script.py
```

---

## 7. Checking Error and Output Files

We regularly check:
- `.out` file → confirms job progress, print statements, timings  
- `.err` file → Python tracebacks, missing module errors, or resource issues  

After each job, we:
1. Inspect `.err` first for exceptions.  
2. Then check `.out` for completion or partial outputs.  
3. Modify script or SLURM parameters if needed and resubmit.

---

## 8. Best Practices

- Use `/scratch` for large jobs, `/home` for scripts.  
- Keep your working directory clean.  
- Always check `.err` and `.out` after each job.  
- Use `tail -f` during long jobs to monitor progress.  
- Document key commands in a simple `commands_log.txt`.

---

## 9. Typical Workflow

```bash
# 1. Login
ssh USERNAME@login3.stampede3.tacc.utexas.edu

# 2. Upload data
scp -r "LOCAL_PATH" USERNAME@stampede3.tacc.utexas.edu:/scratch/10000/USERNAME/

# 3. Prepare SLURM script
nano run_softcite.slurm

# 4. Submit job
sbatch run_softcite.slurm

# 5. Monitor
squeue -u USERNAME
tail -f softcite_job.out

# 6. Download results
scp USERNAME@stampede3.tacc.utexas.edu:/scratch/10000/USERNAME/output/* LOCAL_PATH
```

---

## 10. References

- [TACC Stampede3 User Guide](https://portal.tacc.utexas.edu/user-guides/stampede3)  
- [TACC Usage Policies](https://www.tacc.utexas.edu/user-services/usage-policies/)  
