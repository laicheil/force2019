# ...

```bash
rclone copy iwana-rxar-gdrive:/force-hackathon-2019/tbg/ /var/tmp/tbg/
tensorboard --logdir

rclone copy iwana-rxar-gdrive:/force-hackathon-2019/data-004/ ../force2019-data-000/data-004/

laicheil.force2019.cli visualize --from ../force2019-data-000/data-004/ --to ../force2019-data-000/data-004-viz/
ls | grep -v zone | xargs rm -v

for f in `seq 0 99`; do mkdir -vp dir_$(printf "%03d" "${f}")_good/; mv -v *_good_${f}.png dir_$(printf "%03d" "${f}")_good/; done
for f in `seq 0 99`; do mkdir -vp dir_$(printf "%03d" "${f}")_bad/; mv -v *_bad_${f}.png dir_$(printf "%03d" "${f}")_bad/; done
```
