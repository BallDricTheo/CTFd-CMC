# CTFd Skill-Based Tracks

Plugin for CTFd 3.8.x that provides:

- `/tracks` Track listing
- `/tracks/<slug>` Track detail
- Track -> Level -> Lab hierarchy
- Progress calculated from existing CTFd `solves`
- Admin MVP at `/admin/tracks`
- Labs reuse existing CTFd challenges; no change to challenge logic

Install by copying this folder to `/opt/CTFd-custom-plugins/ctf_tracks` on the host where it is bind-mounted into `/opt/CTFd/CTFd/plugins`.
