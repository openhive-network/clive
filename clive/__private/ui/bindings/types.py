from __future__ import annotations

type BindingID = str
type SectionID = str
type KeyboardShortcut = str

BindingSectionDict = dict[BindingID, KeyboardShortcut]
"""Mapping of binding IDs to their key shortcuts."""

BindingsDict = dict[SectionID, BindingSectionDict]
"""Mapping of section IDs to their binding dictionaries."""
