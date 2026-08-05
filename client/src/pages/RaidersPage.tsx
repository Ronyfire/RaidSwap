import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  getRaiders,
  createRaider,
  updateRaider,
  deleteRaider,
  type Raider,
  type RaiderInput,
} from "../api/raiders";
import { RaiderList } from "../components/raiders/RaiderList";
import { RaiderForm } from "../components/raiders/RaiderForm";
import { RosterImportForm } from "../components/raiders/RosterImportForm";
import { Modal } from "../components/Modal";

export function RaidersPage() {
  const { t } = useTranslation();
  const [raiders, setRaiders] = useState<Raider[]>([]);
  const [editing, setEditing] = useState<Raider | "new" | null>(null);
  const [removing, setRemoving] = useState<Raider | null>(null);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    try {
      setRaiders(await getRaiders());
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.unknownError"));
    }
  }

  async function handleSubmit(data: RaiderInput) {
    try {
      if (editing && editing !== "new") {
        await updateRaider(editing.id, data);
      } else {
        await createRaider(data);
      }
      setEditing(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.unknownError"));
    }
  }

  async function handleConfirmRemove() {
    if (!removing) return;
    try {
      await deleteRaider(removing.id);
      setRemoving(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.unknownError"));
    }
  }

  return (
    <section className="p-8 px-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-semibold mb-1">{t("raidersPage.title")}</h1>
          <div className="text-[13px] text-text-muted">
            {t("raidersPage.raiderCount", { count: raiders.length })}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setImporting(true)}
            className="border border-border-strong rounded px-4.5 py-2.5 text-text-muted font-bold text-[13px]"
          >
            {t("raidersPage.importRoster")}
          </button>
          <button
            onClick={() => setEditing("new")}
            className="bg-accent border-none rounded px-4.5 py-2.5 text-accent-ink font-bold text-[13px]"
          >
            {t("raidersPage.addRaider")}
          </button>
        </div>
      </div>

      {error && (
        <p role="alert" className="text-danger text-sm mb-4">
          {error}
        </p>
      )}

      <div className="flex flex-col gap-6">
        <div>
          <h2 className="font-heading text-[13px] font-semibold text-text-muted uppercase tracking-wide mb-2.5">
            {t("raidersPage.active", { count: raiders.filter((r) => r.status === "active").length })}
          </h2>
          <RaiderList
            raiders={raiders.filter((r) => r.status === "active")}
            onEdit={setEditing}
            onRemove={setRemoving}
          />
        </div>
        <div>
          <h2 className="font-heading text-[13px] font-semibold text-text-muted uppercase tracking-wide mb-2.5">
            {t("raidersPage.bench", { count: raiders.filter((r) => r.status === "bench").length })}
          </h2>
          <RaiderList
            raiders={raiders.filter((r) => r.status === "bench")}
            onEdit={setEditing}
            onRemove={setRemoving}
          />
        </div>
      </div>

      {editing && (
        <Modal onClose={() => setEditing(null)}>
          <RaiderForm
            key={editing === "new" ? "new" : editing.id}
            initial={editing === "new" ? undefined : editing}
            onSubmit={handleSubmit}
            onCancel={() => setEditing(null)}
          />
        </Modal>
      )}

      {importing && (
        <Modal onClose={() => setImporting(false)}>
          <RosterImportForm
            onDone={() => {
              setImporting(false);
              load();
            }}
            onCancel={() => setImporting(false)}
          />
        </Modal>
      )}

      {removing && (
        <Modal onClose={() => setRemoving(null)}>
          <div className="font-heading font-semibold text-base mb-2.5">
            {t("raidersPage.removeTitle")}
          </div>
          <div className="text-[13.5px] text-text-muted mb-5">
            {t("raidersPage.removeBody", { name: removing.name })}
          </div>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setRemoving(null)}
              className="border border-border-strong rounded px-4 py-2 text-text-muted text-[13px]"
            >
              {t("common.cancel")}
            </button>
            <button
              onClick={handleConfirmRemove}
              className="bg-danger-strong border-none rounded px-4 py-2 text-accent-ink font-bold text-[13px]"
            >
              {t("common.remove")}
            </button>
          </div>
        </Modal>
      )}
    </section>
  );
}
