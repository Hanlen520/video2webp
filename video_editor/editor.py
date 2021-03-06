# from video_editor.actions import CutAction, CompressAction, RemoveAudioAction, SpeedupAction,WebpAction,ExportAuidoAction,GifAction
from video_editor.actions import WebpAction,ExportAuidoAction,GifAction,ExportJpgAction
from video_editor.utils import join_video_list
import tempfile
from shutil import copyfile
import os
import time


class VideoEditor:

    def __init__(self, video_path, video_length, real_path):
        self.video_path = video_path
        self.real_path = real_path
        self.video_length = video_length
        self.splits = [Split(video_path, 0, video_length,real_path)]

    def add_split(self, time):
        # Find new split position
        # print(self.splits)
        k = len(self.splits)
        for i, split in enumerate(self.splits):
            if split.end_time > time:
                k = i
                break

        # Create the new split
        split = self.splits[k]
        new_split = split.copy()
        new_split.end_time = time
        self.splits.insert(k, new_split)

        # Edit affected split
        split.start_time = time

    def update_split(self, split_id, config):
        split = self.splits[split_id]
        split.config = config

    def get_splits(self):
        return self.splits

    def get_split_config(self, split_id):
        return self.splits[split_id].config

    def merge_split_with_next(self, split_id):
        split = self.splits[split_id]
        removed_split = self.splits.pop(split_id + 1)
        split.end_time = removed_split.end_time

    def merge_split_with_previous(self, split_id):
        split = self.splits[split_id]
        removed_split = self.splits.pop(split_id - 1)
        split.start_time = removed_split.start_time

    def export_split_webp(self, split_id):
        self.splits[split_id].export('webp')

    def export_split_gif(self, split_id):
        self.splits[split_id].export('gif')

    # def export_and_join_splits(self, split_ids, output_file):
    #     *_, video_extension = self.video_path.split('/')[-1].split(".")
    #
    #     with tempfile.TemporaryDirectory() as dir_path:
    #         dir_path = dir_path.replace("\\", "/")
    #         list_file_path = "{}/list_file.txt".format(dir_path)
    #
    #         with open(list_file_path, "wt") as list_file:
    #
    #             for split_id in split_ids:
    #                 split_tmp_output = "{}/{}.{}".format(dir_path, split_id, video_extension)
    #                 self.splits[split_id].export(split_tmp_output, force_reencode=True)
    #                 list_file.write('file {}.{}\n'.format(split_id, video_extension))
    #
    #         succ, msg = join_video_list(list_file_path, output_file)
    #         if not succ:
    #             print("JOIN SPLITS FAILED\n", msg)

    def export_audio(self,output_path):
        action = ExportAuidoAction(self.video_path,output_path)
        action.run()

    def export_jpg(self,output_path,position):
        action = ExportJpgAction(self.video_path, output_path, position)
        action.run()


class Split:

    """
    Example config
    {
      'reencode': False,
      'compress': True,
      'removeaudio': False,
      'speedup': {
        'factor': 2,
        'dropframes': True,
      }
    }
    """

    def __init__(self, video_path, start_time, end_time,real_path):
        self.video_path = video_path
        self.start_time = start_time
        self.end_time = end_time
        self.real_path = real_path
        self.config = dict()

    @property
    def duration(self):
        return self.end_time - self.start_time

    def export(self, act='webp'):
        def add_extension(file_path, suffix):
            # folder = os.path.dirname(file_path)
            # print(folder)
            # video_name= self.video_path.split('/')[-1].split(".")[0]
            # print(os.path.join(folder, video_name))
            fileName = os.path.splitext(file_path)[0] + \
                       str(time.strftime("%Y%m%d%H%M%S", time.localtime())) + suffix
            # print(fileName)
            return fileName

        if act == 'webp':
            tmp_out = add_extension(self.video_path, '.webp')
            out = add_extension(self.real_path, '.webp')
            action = WebpAction(self.video_path, tmp_out,
                                self.start_time, self.end_time)
            succ, msg = action.run()
        elif act == 'gif':
            tmp_out = add_extension(self.video_path, '.gif')
            out = add_extension(self.real_path, '.gif')
            action = GifAction(self.video_path, tmp_out,
                               self.start_time, self.end_time)
            succ, msg = action.run()

        if not succ:
            return print("CUT ACTION FAILED\n", msg)

        copyfile(tmp_out, out)


        # # Get config values
        # conf_reencode = True if force_reencode else self.config.get('reencode', False)
        # conf_compress = self.config.get('compress', False)
        # conf_remove_audio = self.config.get('removeaudio', False)
        # conf_speedup = self.config.get('speedup', False)

        # # Get video extension and name
        # *video_name, video_extension = self.video_path.split('/')[-1].split(".")
        # video_name = ".".join(video_name)
        # print(video_name)
        # # Create temp folder
        # with tempfile.TemporaryDirectory() as dir_path:
            # dir_path = dir_path.replace("\\", "/")
            # tmp_output_path = "{}/{}_{}_{}".format(dir_path, video_name, self.start_time, self.end_time)

            # Cut split
            # action = CutAction(self.video_path, add_extension(tmp_output_path),
            #                    self.start_time, self.end_time, reencode=conf_reencode)



            # # Compress split
            # if conf_compress:
            #     input_path = add_extension(tmp_output_path)
            #     tmp_output_path += '_C'
            #     action = CompressAction(input_path, add_extension(tmp_output_path))
            #     succ, msg = action.run()
            #     if not succ:
            #         return print("COMPRESS ACTION FAILED\n", msg)
            #
            # # Remove audio from split
            # if conf_remove_audio:
            #     input_path = add_extension(tmp_output_path)
            #     tmp_output_path += '_NA'
            #     action = RemoveAudioAction(input_path, add_extension(tmp_output_path))
            #     succ, msg = action.run()
            #     if not succ:
            #         return print("REMOVE AUDIO ACTION FAILED\n", msg)
            #
            # # Speedup split
            # if conf_speedup and isinstance(conf_speedup, dict):
            #     factor = self.config['speedup'].get('factor', 1)
            #     drop_frames = self.config['speedup'].get('dropframes', True)
            #     input_path = add_extension(tmp_output_path)
            #     tmp_output_path += '_SU'
            #     action = SpeedupAction(input_path, add_extension(tmp_output_path), factor, drop_frames)
            #     succ, msg = action.run()
            #     if not succ:
            #         return print("SPEEDUP ACTION FAILED\n", msg)

            # Copy final video to output path
            # copyfile(webp_extension(tmp_output_path), output_path)


    def copy(self):
        split_copy = Split(self.video_path, self.start_time, self.end_time,self.real_path)
        split_copy.config = self.config
        return split_copy

    def get_split_time(self):
        seconds = self.end_time-self.start_time
        return "{:.2f}".format(seconds / 1000)




