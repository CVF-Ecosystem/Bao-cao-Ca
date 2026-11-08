# Consistent local dialog dismissal

Status: LOCKED_FOR_ADMISSION
Date: 2026-11-08
Version: included in1.10.1/schema4

Operator requests top-right X-close and clicking outside a dialog to hide it, replacing mandatory navigation to bottom Cancel. Extend current FLEX with F5 only; existing reader amendmentc6ab54b7 and accepted source/F3 proof remain frozen.

All normal application modal dialogs expose one visible type=button X in upper-right with aria-label Đóng hộp thoại and clear keyboardfocus, reachable while dialog is scrolled. Backdrop pointerdown AND pointerup must both target backdrop itself; clicks inside or dragging from inside to outside do not dismiss. Escape uses the same close dispatcher. Plain new-shift chooser shown in screenshot closes immediately without creating/opening a report or changing day/shift. X, backdrop and Esc cancel pending import/plans through their existing owner (personnelCancel/cancelLocalOperation), clear correct nonce/generation and cannot allow late responses to reopen a dismissed dialog. Never bypass confirmation/save.

Block requested dismissal while saving/uploading/localBusy/personnelConfirming/printBusy. Existing action/success buttons retain explicit handlers; do not globally replace closeModal with user-discard logic that breaks successful workflows. Do not clear/save/reset the underlying report dirty state merely for dismissal; existing draft autosave semantics remain. Temporary date/file/picker/preview choices may cancel just like their existing Hủy owner; do not prompt for unchanged/default/programmatically suggested values. If an editable catalog/team/template business-data form has actual user edits not saved, request discard confirmation before requested dismissal; refusal keeps DOM/nonce/editor intact. Search inputs and temporary selection controls are not catalog edits.

Capture opener before mounting first modal; nested re-render preserves original opener. Restore focus on dismissal only if opener is still connected and usable, otherwise use a meaningful existing fallback. Close control remains visible but disabled/guarded while busy, no overlapping title/actions and no appearance in printed output. Existing print template/CSS print behavior untouched except explicit hiding of new X control.

Implement using shared existing modal/decorateLocalModal/safeEscape owners, modest scoped CSS and focused meaningful tests: immediate X/backdrop/Esc closure; inside/drag does not close; pending import/localplan cancellation and late response guard; busy refusal; dirty business-form refuse/confirm; unchanged/default form no needless confirmation; focus return and duplicate-close decoration avoidance. Verify newshift X/backdrop on the same one headed session as import F4; synthetic UI screenshots only, no private row images. No broad testing or new dependencies.
