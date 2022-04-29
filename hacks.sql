-- Hacky solutions to solve problems during development
select setval('public.human_humanid_seq'::regclass, max(humanid)) from human;