#!/usr/bin/env python3

# Copyright (c) 2016, Ruslan Baratov
# All rights reserved.

import argparse
import hashlib
import os
import platform
import requests
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import zipfile

print(
    'Python version: {}.{}'.format(
        sys.version_info.major, sys.version_info.minor
     )
)

parser = argparse.ArgumentParser(
    description='Install dependencies for CI testing'
)

args = parser.parse_args()

class FileToDownload:
  def __init__(self, url, sha1, local_path, unpack_dir):
    self.url = url
    self.sha1 = sha1
    self.local_path = local_path
    self.unpack_dir = unpack_dir

    self.download()
    self.unpack()

  def download(self):
    ok = self.hash_match()
    if ok:
      print('File already downloaded: {}'.format(self.local_path))
    else:
      self.real_file_download()
      assert(self.hash_match() == True)

  def hash_match(self):
    if not os.path.exists(self.local_path):
      print('File not exists: {}'.format(self.local_path))
      return False
    sha1_of_file = hashlib.sha1(open(self.local_path, 'rb').read()).hexdigest()
    ok = (sha1_of_file == self.sha1)
    if ok:
      return True
    else:
      print('SHA1 mismatch for file {}:'.format(self.local_path))
      print('  {} (real)'.format(sha1_of_file))
      print('  {} (expected)'.format(self.sha1))
      return False

  def real_file_download(self):
    max_retry = 3
    for i in range(max_retry):
      try:
        self.real_file_download_once()
        print('Done')
        return
      except Exception as exc:
        print('Exception catched ({}), retry... ({} of {})'.format(exc, i+1, max_retry))
        time.sleep(60)
    sys.exit('Download failed')

  # http://stackoverflow.com/a/16696317/2288008
  def real_file_download_once(self):
    print('Downloading:\n  {}\n  -> {}'.format(self.url, self.local_path))
    r = requests.get(self.url, stream=True)
    if not r.ok:
      raise Exception('Downloading failed: {}'.format(self.url))
    with open(self.local_path, 'wb') as f:
      for chunk in r.iter_content(chunk_size=16*1024):
        if chunk:
          f.write(chunk)

  def unpack(self):
    print('Unpacking {}'.format(self.local_path))
    if self.url.endswith('.tar.gz'):
      tar_archive = tarfile.open(self.local_path)
      tar_archive.extractall(path=self.unpack_dir)
      tar_archive.close()
    elif self.url.endswith('.zip'):
      zip_archive = zipfile.ZipFile(self.local_path)
      zip_archive.extractall(path=self.unpack_dir)
      zip_archive.close()
    elif self.url.endswith('.bin'):
      os.chmod(self.local_path, os.stat(self.local_path).st_mode | stat.S_IEXEC)
      last_cwd = os.getcwd()
      os.chdir(self.unpack_dir)
      devnull = open(os.devnull, 'w') # subprocess.DEVNULL is not available for Python 3.2
      subprocess.check_call(android_archive_local, stdout=devnull)
      os.chdir(last_cwd)
    else:
      sys.exit('Unknown archive format')

### Parse toolchain name

toolchain = os.getenv('TOOLCHAIN')
if toolchain is None:
  toolchain = ''
  print('** WARNING ** Environment variable TOOLCHAIN is empty')

is_android = toolchain.startswith('android-')
is_ninja = toolchain.startswith('ninja-')

### Prepare directories

ci_dir = os.path.join(os.getcwd(), '_ci')

if not os.path.exists(ci_dir):
  os.mkdir(ci_dir)

cmake_archive_local = os.path.join(ci_dir, 'cmake-version.archive')
if os.getenv('TRAVIS'):
  android_archive_local = os.path.join(ci_dir, 'android.tar.gz')
else:
  android_archive_local = os.path.join(ci_dir, 'android.bin')
ninja_archive_local = os.path.join(ci_dir, 'ninja.zip')

expected_files = [
    cmake_archive_local, android_archive_local, ninja_archive_local
]

for i in os.listdir(ci_dir):
  dir_item = os.path.join(ci_dir, i)
  expected = (dir_item in expected_files)
  if os.path.isdir(dir_item):
    print('Removing directory: {}'.format(dir_item))
    shutil.rmtree(dir_item)
  elif not expected:
    print('Removing file: {}'.format(dir_item))
    os.remove(dir_item)

cmake_dir = os.path.join(ci_dir, 'cmake')
ninja_dir = os.path.join(ci_dir, 'ninja')

### Downloading files

# https://cmake.org/download/
if platform.system() == 'Darwin':
  cmake = FileToDownload(
      'https://cmake.org/files/v3.5/cmake-3.5.2-Darwin-x86_64.tar.gz',
      '3013b2f00d43da6dc38cbcbd21190874a55b3455',
      cmake_archive_local,
      ci_dir
  )
elif platform.system() == 'Linux':
  cmake = FileToDownload(
      'https://cmake.org/files/v3.5/cmake-3.5.2-Linux-x86_64.tar.gz',
      'f85232bd67929c1789bdd2e842a3f3e55c502e4a',
      cmake_archive_local,
      ci_dir
  )
elif platform.system() == 'Windows':
  cmake = FileToDownload(
      'https://cmake.org/files/v3.5/cmake-3.5.2-win32-x86.zip',
      '743bab5d9c82f0b88b418384026804ed986a50c5',
      cmake_archive_local,
      ci_dir
  )
else:
  sys.exit('Unknown system: {}'.format(platform.system()))

def get_android_full_version_url():
  if os.getenv('TOOLCHAIN') == 'android-ndk-r10e-api-19-armeabi-v7a-neon':
    if platform.system() == 'Darwin':
      return 'http://dl.google.com/android/ndk/android-ndk-r10e-darwin-x86_64.bin', 'b57c2b9213251180dcab794352bfc9a241bf2557',
    elif platform.system() == 'Linux':
      return 'http://dl.google.com/android/ndk/android-ndk-r10e-linux-x86_64.bin', 'c685e5f106f8daa9b5449d0a4f21ee8c0afcb2f6',
  if os.getenv('TOOLCHAIN') == 'android-ndk-r11c-api-19-armeabi-v7a-neon':
    if platform.system() == 'Darwin':
      return 'http://dl.google.com/android/repository/android-ndk-r11c-darwin-x86_64.zip', '4ce8e7ed8dfe08c5fe58aedf7f46be2a97564696',
    elif platform.system() == 'Linux':
      return 'http://dl.google.com/android/repository/android-ndk-r11c-linux-x86_64.zip', 'de5ce9bddeee16fb6af2b9117e9566352aa7e279',
  sys.exit('Android supported only for Linux and OSX')

def get_android_url():
  if os.getenv('TRAVIS'):
    if os.getenv('TOOLCHAIN') == 'android-ndk-r10e-api-19-armeabi-v7a-neon':
      if platform.system() == 'Linux':
        return 'https://github.com/hunter-packages/android-ndk/releases/download/v1.0.0/android-ndk-r10e-arm-linux-androideabi-4.9-gnu-libstdc.-4.9-armeabi-v7a-android-19-arch-arm-Linux.tar.gz', '847177799b0fe4f7480f910bbf1815c3e3fed0da'      if platform.system() == 'Darwin':
        return 'https://github.com/hunter-packages/android-ndk/releases/download/v1.0.0/android-ndk-r10e-arm-linux-androideabi-4.9-gnu-libstdc.-4.9-armeabi-v7a-android-19-arch-arm-Darwin.tar.gz', 'e568e9a8f562e7d1bc06f93e6f7cc7f44df3ded2'
    if os.getenv('TOOLCHAIN') == 'android-ndk-r11c-api-19-armeabi-v7a-neon':
      if platform.system() == 'Linux':
        return 'https://github.com/hunter-packages/android-ndk/releases/download/v1.0.0/android-ndk-r11c-arm-linux-androideabi-4.9-gnu-libstdc.-4.9-armeabi-v7a-android-19-arch-arm-Linux.tar.gz', 'b90d03d11cc1c5770e7851924a60e9819b578960'
      if platform.system() == 'Darwin':
        return 'https://github.com/hunter-packages/android-ndk/releases/download/v1.0.0/android-ndk-r11c-arm-linux-androideabi-4.9-gnu-libstdc.-4.9-armeabi-v7a-android-19-arch-arm-Darwin.tar.gz', '07f2425fa99377a678949314330ec7e5ebc597f8'
  return get_android_full_version_url()

if is_android:
  url, sha1 = get_android_url()
  FileToDownload(url, sha1, android_archive_local, ci_dir)

if is_ninja:
  ninja = FileToDownload(
      'https://github.com/ninja-build/ninja/releases/download/v1.6.0/ninja-win.zip',
      'e01093f6533818425f8efb0843ced7dcaabea3b2',
      ninja_archive_local,
      ci_dir
  )

### Unify directories

for i in os.listdir(ci_dir):
  src = os.path.join(ci_dir, i)
  if i.startswith('cmake') and os.path.isdir(src):
    macosx_contents = os.path.join(src, 'CMake.app', 'Contents')
    if os.path.isdir(macosx_contents):
      os.rename(macosx_contents, cmake_dir)
    else:
      os.rename(src, cmake_dir)

  if i == 'ninja.exe':
    os.mkdir(ninja_dir)
    os.rename(src, os.path.join(ninja_dir, i))
