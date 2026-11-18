import { Button } from "@/components/ui/button";
import { Textarea } from "./components/ui/textarea";
import SideMenu from "./layout/SideMenu";
import {
  Message,
  MessageAvatar,
  MessageContent,
} from "./components/ui/message";
import { Avatar, AvatarFallback, AvatarImage } from "./components/ui/avatar";
import { Bubble, BubbleContent } from "./components/ui/bubble";
import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEventHandler,
} from "react";
import { chatHistory, deleteFile, documents, upload } from "./api";
import type { ChatMessage, UploadedFile, UploadItem } from "./types/chat";
import UserMessageItem from "./components/UserMessageItem";
import AIMessageItem from "./components/AIMessageItem";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupTextarea,
} from "./components/ui/input-group";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./components/ui/dropdown-menu";
import { ArrowUpIcon, PaperclipIcon, PlusIcon } from "lucide-react";
import AttachmentItem from "./components/AttachmentItem";
import { toast } from "./components/ui/toast";

const SESSION_ID = "4c7a0443-28ce-451f-b3dd-0f183b3adf7d";

const App = () => {
  // 获取消息列表
  const [msgList, setMsgList] = useState<ChatMessage[]>([]);
  const fetchMessages = async () => {
    const res = await chatHistory(SESSION_ID);
    setMsgList(res);
  };

  // 获取上传了的文档列表
  const fetchDocuments = async () => {
    const res = await documents();
    setUploadedFiles(res);
  };

  // 流式输出自动向下滚动
  const scrollRef = useRef(null);
  useEffect(() => {
    const el: any = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [msgList]);
  useEffect(() => {
    // 初始化获取这个session的msg
    fetchMessages();

    // fetchDocuments();

    const el: any = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, []);

  // 用户输入
  const [userInput, setUserInput] = useState<string>();
  const handleUserInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    setUserInput(e.target.value);
  };
  const handleUserKeyDown = async (e: React.KeyboardEvent) => {
    const key = e.key;
    const isAlt = e.altKey;
    const isCtrl = e.ctrlKey;

    // Enter: 发送用户消息
    if (key === "Enter" && !isAlt && !isCtrl) {
      e.preventDefault();
      if (userInput?.length) {
        // 发送消息
        sendMsg();
      }
    }

    // ctrl+Enter: 输入换行
    if (key === "Enter" && isCtrl) setUserInput((prev) => prev + "\n");
  };

  // 发送消息
  const sendMsg = async () => {
    // 提交前先判断是否有还没上传完的文件
    const uploading = uploadItems.some((u) => u.status === "uploading");
    const failed = uploadItems.some((u) => u.status === "error");

    if (uploading) {
      toast.add({
        type: "info",
        description: "文件还在上传，请稍候再发送",
      });
      return;
    }
    if (failed) {
      toast.add({
        type: "info",
        description: "有文件上传失败，请重试或移除后再发送",
      });
      return;
    }

    // 1 立即显示用户消息
    setMsgList((prev) => [
      ...prev,
      { role: "user", content: userInput as string, sessionId: SESSION_ID },
    ]);
    setUserInput(""); // 清空用户输入

    // 2. 准备一个空的 assistance 消息占位,用于逐字填充
    const assistanceId = `a_${Date.now()}`;

    // 3 发起流式请求
    const res = await fetch("http://localhost:8000/api/chat/stream", {
      method: "post",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sessionId: SESSION_ID,
        content: userInput,
        uploaded_doc: uploadItems.map((item) => ({
          doc_id: item.doc_id,
          filename: item.filename,
          original_filename: item.original_filename,
        })),
      }),
    });

    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? ""; // 最后一行可能不完整，留到下次

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data: ")) continue;

        const jsonStr = trimmed.slice(6);
        if (jsonStr === "[DONE]") continue;

        try {
          const data = JSON.parse(jsonStr);
          if (data.type === "token") {
            // 如果占位AI消息不存在,就建一个新的ai消息;如果存在,就逐字补充内容
            setMsgList((prev) =>
              prev.find((m) => m.id === assistanceId)
                ? prev.map((m) =>
                    m.id === assistanceId
                      ? { ...m, content: m.content + data.content }
                      : m,
                  )
                : [
                    ...prev,
                    {
                      sessionId: SESSION_ID,
                      content: data.content,
                      role: "assistant",
                      id: assistanceId,
                    },
                  ],
            );
          } else if (data.type === "done") {
            // 可选：结束态处理
          } else if (data.type === "error") {
            console.error("流错误:", data.content);
          }
        } catch (e) {
          // 单行解析失败不中断整个流
          console.warn("跳过无法解析的行:", jsonStr);
        }
      }
    }

    // 每次发送消息后清空文件列表
    setFiles([]);
    setUploadItems([]);
    setUploadedFiles([]);
  };

  // 上传文件
  const inputRef = useRef(null);
  const [files, setFiles] = useState<File[]>([]);
  const [uploadItems, setUploadItems] = useState<UploadItem[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  // input 组件 file change
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(Array.from(e.target.files ?? []));
    setUploadItems(
      Array.from(e.target.files ?? []).map((file) => ({
        status: "uploading",
        original_filename: file.name,
        filename: "",
        doc_id: 0,
      })),
    );
  };
  // 上传按钮
  const handleUploadFile = async () => {
    // @ts-ignore
    inputRef.current.click();
  };
  // 提交上传接口
  const handleSubmitFiles = async () => {
    // 需要上传的文件
    const toUpload = files.filter(
      (file) => !uploadedFiles.some((o) => o.original_filename === file.name),
    );
    if (!toUpload.length) return;

    const formData = new FormData();
    for (const file of toUpload) {
      formData.append("files", file);
    }

    const docs: UploadedFile[] = await upload(formData);

    setUploadItems((prev) =>
      prev.map((item) => {
        const doc = docs.find(
          (d) => d.original_filename === item.original_filename,
        );
        return doc
          ? {
              ...item,
              status: "done",
              filename: doc.filename,
              doc_id: doc.doc_id,
            }
          : item;
      }),
    );
    setFiles((prev) =>
      prev.filter(
        (file) => !docs.some((doc) => doc.original_filename === file.name),
      ),
    );
    setUploadedFiles((prev) => [...prev, ...docs]);
  };
  // 删除文件
  const handleDeleteFile = async (doc_id: number) => {
    const res = await deleteFile(doc_id);
    setUploadedFiles((prev) => prev.filter((file) => file.doc_id !== doc_id));
  };
  useEffect(() => {
    handleSubmitFiles();
  }, [files]);
  useEffect(() => {
    console.log("上传了的文件", uploadedFiles);
  }, [uploadedFiles]);
  useEffect(() => {
    console.log("uploadItems", uploadItems);
  }, [uploadItems]);

  return (
    <>
      <div className="flex">
        <div className="flex-1">
          <SideMenu />
        </div>
        <div
          className="flex-4 flex justify-center"
          ref={scrollRef}
          style={{ height: "100vh", overflowY: "auto" }}
        >
          <div className="w-[70%]">
            <div className="flex  flex-col gap-6 py-12">
              {msgList.map((msg) => {
                if (msg.role === "user")
                  return <UserMessageItem msg={msg}></UserMessageItem>;
                else if (msg.role === "assistant" || msg.role === "ai")
                  return <AIMessageItem msg={msg}></AIMessageItem>;
              })}
            </div>
            <div className="sticky bottom-0 bg-white pb-[20px]">
              {files.map((file) => (
                <AttachmentItem file={file} deletable={false}></AttachmentItem>
              ))}
              {uploadedFiles.map((file) => (
                <AttachmentItem
                  file={file}
                  deletable={true}
                  onDelete={handleDeleteFile}
                ></AttachmentItem>
              ))}
              <InputGroup>
                <input
                  className="hidden"
                  ref={inputRef}
                  type="file"
                  multiple
                  onChange={handleFileChange}
                />
                <div className="h-14 w-full px-3 py-2.5">
                  <InputGroupTextarea
                    value={userInput}
                    onChange={handleUserInputChange}
                    onKeyDown={handleUserKeyDown}
                  />
                  {/* <Textarea
                    value={userInput}
                    onChange={handleUserInputChange}
                    onKeyDown={handleUserKeyDown}
                  /> */}
                </div>
                <InputGroupAddon align="block-end" className="pt-1">
                  <DropdownMenu>
                    <DropdownMenuTrigger
                      render={
                        <InputGroupButton
                          aria-label="Add files"
                          type="button"
                          size="icon-sm"
                          variant="outline"
                        >
                          <PlusIcon />
                        </InputGroupButton>
                      }
                    />
                    <DropdownMenuContent
                      align="start"
                      side="top"
                      className="w-44"
                    >
                      <DropdownMenuItem onClick={handleUploadFile}>
                        <PaperclipIcon />
                        上传文件
                      </DropdownMenuItem>
                      {/* <DropdownMenuSeparator />
                      <DropdownMenuItem>
                        <ImageIcon />
                        Create Image
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <TelescopeIcon />
                        Deep Research
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <GlobeIcon />
                        Web Search
                      </DropdownMenuItem> */}
                    </DropdownMenuContent>
                  </DropdownMenu>
                  <InputGroupButton
                    type="submit"
                    variant="default"
                    size="icon-sm"
                    // disabled={!nextMessage || isBusy}
                    className="ml-auto"
                    onClick={sendMsg}
                  >
                    <ArrowUpIcon />
                    <span className="sr-only">Send</span>
                  </InputGroupButton>
                </InputGroupAddon>
              </InputGroup>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default App;
