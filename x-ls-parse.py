import re
import io
import subprocess
class Demo:
    def run(self, *args, timeout=2):
        # log.debug('docker.run: {}'.format(cmd))
        res = subprocess.run(args, capture_output=True, timeout=timeout)
        res.check_returncode()
        assert res.stderr == b""
        fp = io.BytesIO(res.stdout)
        lines = fp.readlines()
        return lines

    def demo(self, top):
        lines = self.run(
            "/bin/ls", "-anL", "--full-time", top
        )

        file_re1 = r"""
^
(?P<perms>[\-bcdlps][\-rwxsStT]{9})\+?\s+
(?P<links>\d+)\s+
(?P<uid>\d+)\s+
(?P<gid>\d+)\s+
(?P<devmaj>\d+),\s+(?P<devmin>\d+)\s+
(?P<date>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(\.\d+)?)
(?P<datezone>(\.\d+)?\s+\+\d{4})\s+
(?P<name>.*)
"""
        file_re2 = r'''
^
(?P<perms>[\-bcdlps][\-rwxsStT]{9})\+?\s+
(?P<links>\d+)\s+
(?P<uid>\d+)\s+
(?P<gid>\d+)\s+
(?P<size>\d+)\s+
(?P<date>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(\.\d+)?)
(?P<datezone>(\.\d+)?\s+\+\d{4})\s+
(?P<name>.*)
'''

        rfile_re1 = re.compile(file_re1, re.VERBOSE)
        rfile_re2 = re.compile(file_re2, re.VERBOSE)
        result = []
        for line in lines:
            line = line.strip().decode()
            if not line or line[:6] == 'total ':
                continue
            rm = rfile_re1.match(line)
            if not rm:
                rm = rfile_re2.match(line)
            if not rm:
                print('bang', line)
                continue
        #print(rm.groupdict(), rm.span())
        #print(line)

def main():
    cls = Demo()
    cls.demo('/dev')

main()
