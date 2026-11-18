import { FileCodeIcon, PaperclipIcon, XIcon } from "lucide-react";
import {
  Attachment,
  AttachmentAction,
  AttachmentActions,
  AttachmentContent,
  AttachmentDescription,
  AttachmentMedia,
  AttachmentTitle,
} from "./ui/attachment";
import { formatFileSize } from "@/utils/tools";
import type { UploadedFile } from "@/types/chat";
import { useMemo } from "react";

interface Props {
  file: File | UploadedFile;
  deletable?: boolean;
  onDelete?: (doc_id: number) => void;
}

const AttachmentItem = ({ file, deletable, onDelete }: Props) => {
  const isFile = useMemo(() => file instanceof File, [file]);

  const handleDelete = async () => {
    const target = file as UploadedFile;
    onDelete?.(target.doc_id);
  };

  return (
    <Attachment className="w-full">
      <AttachmentMedia>
        <PaperclipIcon />
      </AttachmentMedia>
      <AttachmentContent>
        <AttachmentTitle>
          {isFile
            ? (file as File).name
            : (file as UploadedFile).original_filename}
        </AttachmentTitle>
        <AttachmentDescription>
          {formatFileSize(file.size)}
        </AttachmentDescription>
      </AttachmentContent>
      {deletable && (
        <AttachmentActions>
          <AttachmentAction
            aria-label="Remove message-renderer.tsx"
            onClick={handleDelete}
          >
            <XIcon />
          </AttachmentAction>
        </AttachmentActions>
      )}
    </Attachment>
  );
};

export default AttachmentItem;
