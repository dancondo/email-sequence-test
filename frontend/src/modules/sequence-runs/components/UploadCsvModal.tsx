import { Modal } from "@/shared/components/Modal";
import { CandidateUpload } from "@/modules/candidates/components/CandidateUpload";
import { CsvUploadResult } from "@/modules/candidates/types";

interface UploadCsvModalProps {
  open: boolean;
  onClose: () => void;
  onUploadComplete: (result: CsvUploadResult) => void;
}

export function UploadCsvModal({
  open,
  onClose,
  onUploadComplete,
}: UploadCsvModalProps) {
  const handleComplete = (result: CsvUploadResult) => {
    onUploadComplete(result);
    onClose();
  };

  return (
    <Modal open={open} onClose={onClose} title="Upload CSV">
      <CandidateUpload onUploadComplete={handleComplete} onCancel={onClose} />
    </Modal>
  );
}
