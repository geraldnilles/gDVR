
vf="scale=trunc(oh*a/2)*2:720"

# Denoise Input
# Noise is not easy for encoders to capture since it is hard to predict.  
# Denoising reduces the comlexity of the image and makes it the compression more
# efficient.
	# This reduced the file size by ~20% hich is very significatn 
#ffmpeg -i rec.mpeg2 -vf $vf,hqdn3d -c:v libx264 -preset medium -crf 20 -c:a libfdk_aac -ac 2 rec-crf20-medium-denoise.mkv 

# Single Thread
# I guess using single core allows for better compression??
	# I also read this is BS, but worth testing
	# Yup, testing showed no improvement
#ffmpeg -i rec.mpeg2 -threads 1 -vf $vf -c:v libx264 -preset medium -crf 20 -c:a libfdk_aac -ac 2 rec-crf20-medium-single_thread.mkv 

# Constant Bitrate
#ffmpeg -i rec.mpeg2 -vf $vf -c:v libx264 -preset medium -b:v 2000k -c:a libfdk_aac -ac 2 rec-2000k.mkv 

# Constant Quality
#ffmpeg -i rec.mpeg2 -vf $vf -c:v libx264 -preset medium -crf 20 -c:a libfdk_aac -ac 2 rec-crf20-medium.mkv 

#ffmpeg -i rec.mpeg2 -vf $vf -c:v libx264 -preset medium -crf 22 -c:a libfdk_aac -ac 2 rec-crf22-medium.mkv 

#ffmpeg -i rec.mpeg2 -vf $vf -c:v libx264 -preset medium -crf 18 -c:a libfdk_aac -ac 2 rec-crf18-medium.mkv 

#ffmpeg -i rec.mpeg2 -vf $vf -c:v libx264 -preset slow -crf 20 -c:a libfdk_aac -ac 2 rec-crf20-slow.mkv

#ffmpeg -i rec.mpeg2 -vf $vf -c:v libx264 -preset veryslow -crf 20 -c:a libfdk_aac -ac 2 rec-crf20-veryslow.mkv 

ffmpeg -i rec.mpeg2 -vf $vf,hqdn3d -c:v libx264 -preset veryslow -crf 20 -c:a libfdk_aac rec-crf20-veryslow-denoise.mkv 

# 2 Pass

#ffmpeg -y -i rec.mpeg2 -vf $vf -c:v libx264 -preset medium -b:v 2000k -pass 1 -c:a libfdk_aac  -f mp4 /dev/null && \
#ffmpeg -i rec.mpeg2 -vf $vf -c:v libx264 -preset medium -b:v 2000k -pass 2 -c:a libfdk_aac  rec-2pass-2000k.mkv


# Simplify Colors (Cartoon effect) Reducing the color depth (and also
# increasing contrast to make it less obvious) again simplifies the input and
# makes the compression better
