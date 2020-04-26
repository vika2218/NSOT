import subprocess
cmds=["git add .", "git commit -m .", "git push origin master"]
for i in cmds:
	op= subprocess.check_output(i, shell=True)
	print(op)
