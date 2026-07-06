from contextlib import nullcontext

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from vitrine.models import Frame


class Command(BaseCommand):
    help = (
        "Sync frame auto-seal state and regenerate dependent seal rows. "
        "Use `enable-all` to set all frames auto_calculate_seal=True before recalculation, "
        "or `sync-selected` to recalculate only frames that are already selected."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            choices=("enable-all", "sync-selected"),
            default="sync-selected",
            help="Sync mode to execute.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview affected frames without writing to the database.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Iterator chunk size while processing frames.",
        )
        parser.add_argument(
            "--frame-id",
            type=int,
            nargs="+",
            help="Process only specific frame IDs.",
        )
        parser.add_argument(
            "--vitrine-id",
            type=int,
            nargs="+",
            help="Process only frames belonging to specific vitrine IDs.",
        )
        parser.add_argument(
            "--no-atomic",
            action="store_true",
            help="Disable per-frame transaction.atomic() wrapper.",
        )

    def handle(self, *args, **options):
        mode = options["mode"]
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]
        use_atomic = not options["no_atomic"]
        base_queryset = self._build_base_queryset(options)

        if batch_size < 1:
            raise CommandError("--batch-size must be >= 1")

        if mode == "enable-all":
            self._enable_all_and_recalculate(base_queryset, dry_run, use_atomic, batch_size)
        else:
            self._recalculate_selected_only(base_queryset, dry_run, use_atomic, batch_size)

    def _build_base_queryset(self, options):
        queryset = Frame.objects.select_related("vitrine_id")
        frame_ids = options.get("frame_id")
        vitrine_ids = options.get("vitrine_id")

        if frame_ids:
            queryset = queryset.filter(pk__in=frame_ids)
        if vitrine_ids:
            queryset = queryset.filter(vitrine_id__in=vitrine_ids)

        return queryset

    def _enable_all_and_recalculate(self, base_queryset, dry_run, use_atomic, batch_size):
        to_enable = base_queryset.filter(auto_calculate_seal=False)
        updated = to_enable.count() if dry_run else to_enable.update(auto_calculate_seal=True)
        processed = self._recalculate_queryset(base_queryset, dry_run, use_atomic, batch_size)
        mode_label = "dry-run enable-all" if dry_run else "enable-all"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode_label} completed: updated={updated}, recalculated={processed}."
            )
        )

    def _recalculate_selected_only(self, base_queryset, dry_run, use_atomic, batch_size):
        selected_frames = base_queryset.filter(auto_calculate_seal=True)
        processed = self._recalculate_queryset(selected_frames, dry_run, use_atomic, batch_size)
        mode_label = "dry-run sync-selected" if dry_run else "sync-selected"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode_label} completed: recalculated={processed}."
            )
        )

    def _recalculate_queryset(self, queryset, dry_run, use_atomic, batch_size):
        processed = 0

        for frame in queryset.iterator(chunk_size=batch_size):
            if dry_run:
                processed += 1
                continue

            context_manager = transaction.atomic() if use_atomic else nullcontext()
            with context_manager:
                frame.run_workflow_save()
            processed += 1

        return processed
