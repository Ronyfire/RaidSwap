import type { ReactNode } from "react";

interface ModalProps {
  children: ReactNode;
  onClose: () => void;
}

export function Modal({ children, onClose }: ModalProps) {
  return (
    <div
      className="fixed inset-0 bg-black/55 flex items-center justify-center z-30"
      onClick={onClose}
    >
      <div
        className="w-[380px] max-w-[90vw] bg-surface border border-border rounded-md p-5"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
}
