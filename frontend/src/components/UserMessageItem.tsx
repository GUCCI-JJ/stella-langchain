import React from "react";
import { Message, MessageAvatar, MessageContent } from "./ui/message";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Bubble, BubbleContent } from "./ui/bubble";
import type { ChatMessage } from "@/types/chat";

const UserMessageItem = React.memo(({ msg }: { msg: ChatMessage }) => (
  <Message align="end">
    <MessageAvatar>
      <Avatar>
        <AvatarImage src="/images/avatar.jpg" alt="@avatar" />
        <AvatarFallback>R</AvatarFallback>
      </Avatar>
    </MessageAvatar>
    <MessageContent>
      <Bubble>
        <BubbleContent>{msg.content}</BubbleContent>
      </Bubble>
    </MessageContent>
  </Message>
));

export default UserMessageItem;
