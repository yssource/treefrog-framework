#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, Meson, RunEnvironment
import os
import pathlib


class AbquantConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_mongoc": [True, False],
        "enable_debug": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "qt:qtdeclarative": True,
        "qt:qttools": True,
        "qt:qtwebsockets": True,
        "with_mongoc": True,
        "enable_debug": True,
    }

    generators = ["cmake", "qmake"]

    def requirements(self):
        self.requires("qt/5.12.6@{}/{}".format("bincrafters", "stable"))
        # self.requires("mongo-c-driver/1.14.0@{}/{}".format("bincrafters", "testing"))
        self.requires("lz4/1.9.2@")

    @property
    def _prefix(self):
        if tools.os_info.is_linux:
            PREFIX = "/usr"
        else:
            PREFIX = "/usr/local"
        return PREFIX

    @property
    def _bindir(self):
        return "{}/bin".format(self._prefix)

    @property
    def _libdir(self):
        return "{}/lib".format(self._prefix)

    @property
    def _includedir(self):
        return "{}/include/treefrog".format(self._prefix)

    @property
    def _datadir(self):
        return "{}/share/treefrog".format(self._prefix)

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "src")

    @property
    def _build_subfolder(self):
        return os.path.join(self.source_folder, "qbuild")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _build_with_qmake(self):
        tools.mkdir(self._build_subfolder)
        with tools.chdir(self._build_subfolder):
            try:
                cmd = "rm -fv .qmake.stash"
                self.output.info(cmd)
                self.run(cmd, run_environment=True)

                path = pathlib.Path("Makefile")
                if path.exists():
                    cmd = "make -k distclean >/dev/null 2>&1"
                    self.output.info(cmd)
                    self.run(cmd, run_environment=True)
            except Exception:
                pass

            self.output.info("Building with qmake")
            with tools.vcvars(
                self.settings
            ) if self.settings.compiler == "Visual Studio" else tools.no_op():
                args = ["{}/corelib.pro".format(self._source_subfolder), "DESTDIR=bin"]

                def _getenvpath(var):
                    val = os.getenv(var)
                    if val and tools.os_info.is_windows:
                        val = val.replace("\\", "/")
                        os.environ[var] = val
                    return val

                value = _getenvpath("CC")
                if value:
                    args += [
                        "QMAKE_CC=" + value,
                        "QMAKE_LINK_C=" + value,
                        "QMAKE_LINK_C_SHLIB=" + value,
                    ]

                value = _getenvpath("CXX")
                if value:
                    args += [
                        "QMAKE_CXX=" + value,
                        "QMAKE_LINK=" + value,
                        "QMAKE_LINK_SHLIB=" + value,
                    ]

                if tools.os_info.is_linux:
                    args += ["-spec linux-clang"]

                if self.settings.arch == "x86_64":
                    args += ["CONFIG+=x86_64"]

                if self.options.enable_debug:
                    args += ["CONFIG+=debug"]
                else:
                    args += ["CONFIG+=release"]

                if self.options.with_mongoc:
                    args += ["shared_mongoc=1"]

                # target.path=\"$LIBDIR\" header.path=\"$INCLUDEDIR\" $ENABLE_GUI $ENABLE_SHARED_MONGOC
                args += [
                    'target.path="{}"'.format(self._libdir),
                    'header.path="{}"'.format(self._includedir),
                ]

                cmd = "qmake %s" % " ".join(args)
                self.output.info(cmd)
                self.run(cmd, run_environment=True)

                # bear make
                if tools.os_info.is_windows:
                    if self.settings.compiler == "Visual Studio":
                        self.run("jom", run_environment=True)
                    else:
                        self.run("mingw32-make", run_environment=True)
                else:
                    cmd = "bear make"
                    self.output.info(cmd)
                    self.run(cmd, run_environment=True)

                self.output.info(
                    'OK, installing... run "sudo make install" in {} directory.'.format(
                        self._build_subfolder
                    )
                )

    def build(self):
        self._build_with_qmake()
