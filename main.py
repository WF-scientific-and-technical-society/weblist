from pan123 import Pan123

if __name__ == "__main__":
    pan = Pan123(readfile=True, input_pwd=True)

    # 登录并检查是否成功
    login_code = pan.login()
    if login_code == 200:
        print("✅ 登录成功")
        pan.show()
        os._exit(0)
    else:
        print(f"❌ 登录失败，错误码: {login_code}")
        os._exit(0)
    while True:
        command = input("\033[91m >\033[0m")
        if command == "ls":
            pan.show()
        if command == "re":
            code = pan.get_dir()
            if code == 0:
                print("刷新目录成功")
            pan.show()
        if command.isdigit():
            if int(command) > len(pan.list) or int(command) < 1:
                print("输入错误")
                continue
            if pan.list[int(command) - 1]["Type"] == 1:
                pan.cdById(pan.list[int(command) - 1]["FileId"])
            else:
                size = pan.list[int(command) - 1]["Size"]
                if size > 1048576:
                    size_print_show = str(round(size / 1048576, 2)) + "M"
                else:
                    size_print_show = str(round(size / 1024, 2)) + "K"
                # print(pan.list[int(command) - 1])
                name = pan.list[int(command) - 1]["FileName"]
                print(name + "  " + size_print_show)
                print("输入1开始下载: ", end="")
                sure = input()
                if sure == "1":
                    pan.download(int(command) - 1)
        elif command[0:9] == "download ":
            if command[9:].isdigit():
                if int(command[9:]) > len(pan.list) or int(command[9:]) < 1:
                    print("输入错误")
                    continue
                if pan.list[int(command[9:]) - 1]["Type"] == 1:
                    print(pan.list[int(command[9:]) - 1]["FileName"])
                    print("将打包下载文件夹，输入1开始下载:", end="")
                    sure = input()
                    if sure != "1":
                        continue
                pan.download(int(command[9:]) - 1)
            else:
                print("输入错误")
        elif command == "exit":
            break
        elif command == "log":
            pan.login()
            pan.get_dir()
            pan.show()

        elif command[0:5] == "link ":
            if command[5:].isdigit():
                if int(command[5:]) > len(pan.list) or int(command[5:]) < 1:
                    print("输入错误")
                    continue
                pan.link(int(command[5:]) - 1)
            else:
                print("输入错误")
        elif command == "upload":
            filepath = input("请输入文件路径：")
            pan.up_load(filepath)
            pan.get_dir()
            pan.show()
        elif command == "share":
            pan.share()
        elif command[0:6] == "delete":
            if command == "delete":
                print("请输入要删除的文件编号：", end="")
                fileNumber = input()
            else:
                if command[6] == " ":
                    fileNumber = command[7:]
                else:
                    print("输入错误")
                    continue
                if fileNumber == "":
                    print("请输入要删除的文件编号：", end="")
                    fileNumber = input()
                else:
                    fileNumber = fileNumber[0:]
            if fileNumber.isdigit():
                if int(fileNumber) > len(pan.list) or int(fileNumber) < 1:
                    print("输入错误")
                    continue
                pan.delete_file(int(fileNumber) - 1)
                pan.get_dir()
                pan.show()
            else:
                print("输入错误")

        elif command[:3] == "cd ":
            path = command[3:]
            pan.cd(path)
        elif command[0:5] == "mkdir":
            if command == "mkdir":
                newPath = input("请输入目录名:")
            else:
                newPath = command[6:]
                if newPath == "":
                    newPath = input("请输入目录名:")
                else:
                    newPath = newPath[0:]
            print(pan.mkdir(newPath))
            pan.get_dir()
            pan.show()

        elif command == "reload":
            pan.read_ini("", "", True)
            print("读取成功")
            pan.get_dir()
            pan.show()
