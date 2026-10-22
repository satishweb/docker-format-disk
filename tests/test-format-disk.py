#!/usr/bin/env python3

import argparse
import sys
import unittest

# The file systems the image can make.
FILE_SYSTEMS = ["ext4", "xfs", "btrfs", "vfat", "exfat", "ntfs"]
# The tools the image needs to work with the devices.
TOOLS = ["mkfs.ext4", "sfdisk", "blkid"]


def run_tests(image_name):
    import docker

    class TestFormatDisk(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.client = docker.from_env()

        def run_command(self, command):
            container = self.client.containers.run(
                image_name, command=command, detach=True, stdout=True, stderr=True
            )
            result = container.wait()
            output = container.logs().decode("utf-8", errors="replace")
            container.remove()
            return result.get("StatusCode"), output

        def test_the_script_is_there(self):
            print("Running the script test...")
            # The arguments are added to the command of the image.
            image = self.client.images.get(image_name)
            command = (image.attrs["Config"].get("Cmd") or []) + ["--help"]
            _, output = self.run_command(command)
            self.assertIn("Usage", output, f"The script did not print its usage: {output}")
            print("Script test passed.")

        def test_the_tools_are_there(self):
            print("Running the tools test...")
            for tool in TOOLS:
                code, output = self.run_command(["/bin/sh", "-c", f"command -v {tool}"])
                self.assertEqual(
                    code, 0, f"The tool {tool} is not in the image: {output}"
                )
            print("Tools test passed.")

        def test_the_file_systems_are_there(self):
            print("Running the file systems test...")
            for file_system in FILE_SYSTEMS:
                code, output = self.run_command(
                    ["/bin/sh", "-c", f"command -v mkfs.{file_system}"]
                )
                self.assertEqual(
                    code,
                    0,
                    f"The file system {file_system} is not in the image: {output}",
                )
            print("File systems test passed.")

    print(f"Checking the image '{image_name}'...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFormatDisk)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the tests for the format disk image.")
    parser.add_argument(
        "--image",
        type=str,
        default="satishweb/docker-format-disk:ci",
        help="The image that is tested",
    )
    args = parser.parse_args()

    run_tests(args.image)
