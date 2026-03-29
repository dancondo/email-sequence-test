import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useCandidateTimeline, useSendReply } from "../hooks";
import { PATHS } from "@/routes/paths";
import { EventType, SequenceRunCandidateEvent } from "../types";
import { RichTextEditor } from "@/shared/components/RichTextEditor";

const EVENT_STYLES: Record<EventType, { bg: string; dot: string; label: string }> = {
  enrolled: { bg: "bg-gray-50", dot: "bg-gray-400", label: "Enrolled" },
  email_scheduled: { bg: "bg-blue-50", dot: "bg-blue-400", label: "Email Scheduled" },
  email_sent: { bg: "bg-green-50", dot: "bg-green-400", label: "Email Sent" },
  email_failed: { bg: "bg-red-50", dot: "bg-red-400", label: "Email Failed" },
  email_canceled: { bg: "bg-yellow-50", dot: "bg-yellow-400", label: "Email Canceled" },
  reply_received: { bg: "bg-purple-50", dot: "bg-purple-400", label: "Reply Received" },
  reply_classified: { bg: "bg-indigo-50", dot: "bg-indigo-400", label: "Reply Classified" },
  reply_sent: { bg: "bg-teal-50", dot: "bg-teal-400", label: "Reply Email Sent" },
  referral_detected: { bg: "bg-amber-50", dot: "bg-amber-400", label: "Referral Detected" },
  referral_handoff_sent: { bg: "bg-orange-50", dot: "bg-orange-400", label: "Referral Handoff Sent" },
  completed: { bg: "bg-green-50", dot: "bg-green-500", label: "Completed" },
  unsubscribed: { bg: "bg-red-50", dot: "bg-red-500", label: "Unsubscribed" },
};

const STATUS_STYLES: Record<string, string> = {
  active: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  replied: "bg-purple-100 text-purple-700",
  interested: "bg-green-100 text-green-700",
  not_interested: "bg-red-100 text-red-700",
  unsubscribed: "bg-red-100 text-red-700",
};

const INTENT_STYLES: Record<string, string> = {
  positive: "bg-green-100 text-green-700",
  interested: "bg-green-100 text-green-700",
  negative: "bg-red-100 text-red-700",
  not_interested: "bg-red-100 text-red-700",
  neutral: "bg-yellow-100 text-yellow-700",
};

function EventMetadata({ event }: { event: SequenceRunCandidateEvent }) {
  const meta = event.metadata;
  if (!meta || Object.keys(meta).length === 0) return null;

  if (event.event_type === "reply_received") {
    const { from_email, subject, body } = meta as {
      from_email?: string;
      subject?: string;
      body?: string;
    };
    return (
      <div className="mt-2 space-y-1 text-xs">
        {from_email && (
          <p className="text-gray-500">
            <span className="font-medium text-gray-600">From:</span> {from_email}
          </p>
        )}
        {subject && (
          <p className="text-gray-500">
            <span className="font-medium text-gray-600">Subject:</span> {subject}
          </p>
        )}
        {body && (
          <div className="mt-1 rounded border border-gray-200 bg-white p-2 text-gray-600">
            <div dangerouslySetInnerHTML={{ __html: body }} />
          </div>
        )}
      </div>
    );
  }

  if (event.event_type === "reply_classified") {
    const { intent, confidence, reasoning } = meta as {
      intent?: string;
      confidence?: number;
      reasoning?: string;
    };
    return (
      <div className="mt-2 space-y-1 text-xs">
        {intent && (
          <p>
            <span
              className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                INTENT_STYLES[intent.toLowerCase()] ?? "bg-gray-100 text-gray-700"
              }`}
            >
              {intent}
            </span>
            {confidence != null && (
              <span className="ml-2 text-gray-400">
                {Math.round(confidence * 100)}% confidence
              </span>
            )}
          </p>
        )}
        {reasoning && (
          <p className="text-gray-500 italic">{reasoning}</p>
        )}
      </div>
    );
  }

  if (event.event_type === "email_scheduled" || event.event_type === "email_sent") {
    const { subject, body } = meta as { subject?: string; body?: string };
    return (
      <div className="mt-2 space-y-1 text-xs">
        {subject && (
          <p className="text-gray-500">
            <span className="font-medium text-gray-600">Subject:</span> {subject}
          </p>
        )}
        {body && (
          <div className="mt-1 rounded border border-gray-200 bg-white p-2 text-gray-600">
            <div dangerouslySetInnerHTML={{ __html: body }} />
          </div>
        )}
      </div>
    );
  }

  if (event.event_type === "reply_sent") {
    const { subject, body } = meta as { subject?: string; body?: string };
    return (
      <div className="mt-2 space-y-1 text-xs">
        {subject && (
          <p className="text-gray-500">
            <span className="font-medium text-gray-600">Subject:</span> {subject}
          </p>
        )}
        {body && (
          <div className="mt-1 rounded border border-gray-200 bg-white p-2 text-gray-600">
            <div dangerouslySetInnerHTML={{ __html: body }} />
          </div>
        )}
      </div>
    );
  }

  if (event.event_type === "referral_detected") {
    const { referred_candidate_email, referred_candidate_name, referral_list_name } =
      meta as {
        referred_candidate_email?: string;
        referred_candidate_name?: string;
        referral_list_name?: string;
      };
    return (
      <div className="mt-2 space-y-1 text-xs">
        <p className="text-gray-600">
          <span className="font-medium">Referred:</span>{" "}
          {referred_candidate_name
            ? `${referred_candidate_name} (${referred_candidate_email})`
            : referred_candidate_email}
        </p>
        {referral_list_name && (
          <p className="text-gray-500">
            Added to list:{" "}
            <span className="font-medium">{referral_list_name}</span>
          </p>
        )}
      </div>
    );
  }

  if (event.event_type === "referral_handoff_sent") {
    const { to_email, referred_candidate_email, referred_candidate_name, subject, body } =
      meta as {
        to_email?: string;
        referred_candidate_email?: string;
        referred_candidate_name?: string;
        subject?: string;
        body?: string;
      };
    return (
      <div className="mt-2 space-y-1 text-xs">
        {to_email && (
          <p className="text-gray-500">
            <span className="font-medium text-gray-600">To:</span> {to_email}
          </p>
        )}
        {referred_candidate_email && (
          <p className="text-gray-500">
            <span className="font-medium text-gray-600">Referred:</span>{" "}
            {referred_candidate_name
              ? `${referred_candidate_name} (${referred_candidate_email})`
              : referred_candidate_email}
          </p>
        )}
        {subject && (
          <p className="text-gray-500">
            <span className="font-medium text-gray-600">Subject:</span> {subject}
          </p>
        )}
        {body && (
          <div className="mt-1 rounded border border-gray-200 bg-white p-2 text-gray-600">
            <div dangerouslySetInnerHTML={{ __html: body }} />
          </div>
        )}
      </div>
    );
  }

  if (event.event_type === "email_canceled") {
    const { canceled_schedule_id } = meta as { canceled_schedule_id?: string };
    if (!canceled_schedule_id) return null;
    return (
      <p className="mt-1 text-xs text-gray-500">
        Schedule <span className="font-mono">{canceled_schedule_id}</span> canceled
      </p>
    );
  }

  if (event.event_type === "email_failed") {
    const { error } = meta as { error?: string };
    if (!error) return null;
    return (
      <p className="mt-1 text-xs text-red-500">{error}</p>
    );
  }

  return null;
}

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

                      <EventMetadata event={event} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Reply Form */}
      {(src.status === "replied" || src.status === "interested" || src.status === "not_interested") && (
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
