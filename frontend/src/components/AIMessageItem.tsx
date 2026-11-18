import type { ChatMessage } from "@/types/chat";
import { AIResponseParser } from "ai-response-parser";
import React from "react";

const AIMessageItem = React.memo(({ msg }: { msg: ChatMessage }) => (
  <div className="markdown-body">
    {/* <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown> */}
    <AIResponseParser content={msg.content}></AIResponseParser>
  </div>
));

export default AIMessageItem;
