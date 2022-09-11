import setuptools

with open("readme.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="open-mcr",
    url = "https://github.com/gutow/open-mcr",
    version="1.3.0dev",
    description="Graphical tool for optical mark recognition for test scoring.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ian Sanders",
    author_email="iansan5653@github.com",
    keywords="omr, optical-mark-recognition, open-educational-resources, " \
             "exam-sheets, exam-scoring",
    license="GPL-3.0+",
    packages=setuptools.find_packages(exclude=("dist","build",)),
    data_files=[
    	('src/assets',['src/assets/icon.ico','src/assets/icon.svg',
                   'src/assets/multiple_choice_sheet_75q.pdf',
                   'src/assets/multiple_choice_sheet_75q.svg',
                   'src/assets/multiple_choice_sheet_150q.pdf',
                   'src/assets/multiple_choice_sheet_150q.svg',
                   'src/assets/social.png', 'src/assets/wordmark.png',
                   'src/assets/wordmark.svg', 'src/assets/manual.md',
                   'src/assets/manual.pdf'])
    ],
    include_package_data=True,
    install_requires=[
        'PyInstaller>=4.6',
        'Pillow==9.2.0',
        'numpy==1.22.0',
        'opencv-python==4.5.4.60',
        'flake8==3.7.8',
        'yapf==0.28.0',
        'pytest==6.2.5',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ]
)