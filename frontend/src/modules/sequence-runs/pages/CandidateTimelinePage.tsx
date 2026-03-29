import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useCandidateTimeline, useSendReply } from "../hooks";
import { PATHS } from "@/routes/paths";
import { EventType } from "../types";
import { RichTextEditor } from "@/shared/components/RichTextEditor";

const EVENT_STYLES: Record<EventType, { bg: string; dot: string; label: string }> = {
  enrolled: { bg: "bg-gray-50", dot: "bg-gray-400", label: "Enrolled" },
  email_scheduled: { bg: "bg-blue-50", dot: "bg-blue-400", label: "Email Scheduled" },
  email_sent: { bg: "bg-green-50", dot: "bg-green-400", label: "Email Sent" },
  email_failed: { bg: "bg-red-50", dot: "bg-red-400", label: "Email Failed" },
  reply_received: { bg: "bg-purple-50", dot: "bg-purple-400", label: "Reply Received" },
  reply_classified: { bg: "bg-indigo-50", dot: "bg-indigo-400", label: "Reply Classified" },
  reply_sent: { bg: "bg-teal-50", dot: "bg-teal-400", label: "Reply Sent" },
  completed: { bg: "bg-green-50", dot: "bg-green-500", label: "Completed" },
  unsubscribed: { bg: "bg-red-50", dot: "bg-red-500", label: "Unsubscribed" },
};

const STATUS_STYLES: Record<string, string> = {
  active: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  replied: "bg-purple-100 text-purple-700",
  unsubscribed: "bg-red-100 text-red-700",
};

export function CandidateTimelinePage() {
  const { id, runId, candidateId } = useParams<{
    id: string;
    runId: string;
    candidateId: string;
  }>();
  const sequenceId = Number(id);
  const runIdNum = Number(runId);
  const candidateIdNum = Number(candidateId);
  const navigate = useNavigate();

  const { data, isLoading } = useCandidateTimeline(
    sequenceId,
    runIdNum,
    candidateIdNum
  );

  const replyMutation = useSendReply(sequenceId, runIdNum, candidateIdNum);
  const [replyBody, setReplyBody] = useState("");

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl p-6">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="mx-auto max-w-4xl p-6">
        <p className="text-red-600">Candidate not found in this run.</p>
      </div>
    );
  }

  const { candidate: src, events } = data;

  return (
    <div className="mx-auto max-w-4xl p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() =>
            navigate(
              PATHS.SEQUENCE_RUN_DETAIL.replace(
                ":id",
                String(sequenceId)
              ).replace(":runId", String(runIdNum))
            )
          }
          className="mb-1 text-sm text-gray-500 hover:text-gray-700"
        >
          &larr; Back to Run
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              {src.candidate.email}
            </h1>
            {src.candidate.name && (
              <p className="text-sm text-gray-500">{src.candidate.name}</p>
            )}
          </div>
          <span
            className={`inline-block rounded-full px-3 py-1 text-sm font-medium ${
              STATUS_STYLES[src.status] ?? ""
            }`}
          >
            {src.status}
          </span>
        </div>
        <p className="mt-1 text-sm text-gray-500">
          Current step: {src.current_step_order} &middot; Enrolled:{" "}
          {new Date(src.created_at).toLocaleString()}
        </p>
      </div>

      {/* Timeline */}
      <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-800">Timeline</h2>

        {events.length === 0 ? (
          <p className="text-gray-500">No events yet.</p>
        ) : (
          <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-3 top-0 h-full w-0.5 bg-gray-200" />

            <div className="space-y-4">
              {events.map((event) => {
                const style = EVENT_STYLES[event.event_type] ?? {
                  bg: "bg-gray-50",
                  dot: "bg-gray-400",
                  label: event.event_type,
                };

                return (
                  <div key={event.id} className="relative flex gap-4 pl-8">
                    {/* Dot */}
                    <div
                      className={`absolute left-1.5 top-2 h-3 w-3 rounded-full ${style.dot}`}
                    />

                    <div
                      className={`flex-1 rounded border border-gray-100 px-3 py-2 ${style.bg}`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-800">
                          {style.label}
                        </span>
                        <span className="text-xs text-gray-400">
                          {new Date(event.occurred_at).toLocaleString()}
                        </span>
                      </div>

                      {event.step_order !== null && (
                        <p className="mt-0.5 text-xs text-gray-500">
                          Step {event.step_order}
                        </p>
                      )}

                      {event.external_message_id && (
                        <p className="mt-0.5 text-xs text-gray-400">
                          Message: {event.external_message_id.substring(0, 20)}
                          ...
                        </p>
                      )}

                      {event.metadata &&
                        Object.keys(event.metadata).length > 0 && (
                          <pre className="mt-1 overflow-auto text-xs text-gray-500">
                            {JSON.stringify(event.metadata, null, 2)}
                          </pre>
                        )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Reply Form */}
      {src.status === "replied" && (
        <div className="mt-6 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-800">
            Send Reply
          </h2>
          <RichTextEditor
            content={replyBody}
            onChange={setReplyBody}
            placeholder="Write your reply..."
          />
          <div className="mt-3 flex items-center gap-3">
            <button
              onClick={() =>
                replyMutation.mutate(replyBody, {
                  onSuccess: () => setReplyBody(""),
                })
              }
              disabled={
                !replyBody.trim() ||
                replyBody === "<p></p>" ||
                replyMutation.isPending
              }
              className="rounded bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {replyMutation.isPending ? "Sending..." : "Send Reply"}
            </button>
            {replyMutation.isError && (
              <span className="text-sm text-red-600">
                Failed to send reply. Please try again.
              </span>
            )}
            {replyMutation.isSuccess && (
              <span className="text-sm text-green-600">Reply sent!</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
